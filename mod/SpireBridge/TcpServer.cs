using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace MimoSpire.Bridge;

// Line-delimited JSON TCP server on localhost. Accept/client loops run on
// background threads; each request is posted to the game main thread via
// GameDispatcher and answered when the main thread completes it.
public sealed class TcpServer
{
    private static readonly TimeSpan GameThreadTimeout = TimeSpan.FromSeconds(10);
    private readonly int _port;
    private TcpListener? _listener;
    private volatile bool _running;

    public TcpServer(int port)
    {
        _port = port;
    }

    public void Start()
    {
        _listener = new TcpListener(IPAddress.Loopback, _port);
        _listener.Start();
        _running = true;
        var thread = new Thread(AcceptLoop) { IsBackground = true, Name = "SpireBridgeAccept" };
        thread.Start();
        BridgeMod.LogInfo($"listening on 127.0.0.1:{_port}");
    }

    public void Stop()
    {
        _running = false;
        try
        {
            _listener?.Stop();
        }
        catch (Exception e)
        {
            BridgeMod.LogErr($"listener stop failed: {e}");
        }
    }

    private void AcceptLoop()
    {
        while (_running)
        {
            TcpClient client;
            try
            {
                client = _listener!.AcceptTcpClient();
            }
            catch (Exception)
            {
                break;
            }
            var thread = new Thread(() => ClientLoop(client)) { IsBackground = true, Name = "SpireBridgeClient" };
            thread.Start();
        }
    }

    private void ClientLoop(TcpClient client)
    {
        using TcpClient _ = client;
        using NetworkStream stream = client.GetStream();
        using var reader = new StreamReader(stream, Encoding.UTF8);
        using var writer = new StreamWriter(stream, Encoding.UTF8) { NewLine = "\n", AutoFlush = true };
        BridgeMod.LogInfo("client connected");
        while (_running)
        {
            string? line;
            try
            {
                line = reader.ReadLine();
            }
            catch (Exception)
            {
                break;
            }
            if (line == null)
            {
                break;
            }
            if (string.IsNullOrWhiteSpace(line))
            {
                continue;
            }
            GameDispatcher? dispatcher = GameDispatcher.Instance;
            if (dispatcher == null)
            {
                Write(writer, Protocol.Error("dispatcher not ready", null));
                continue;
            }
            var tcs = new TaskCompletionSource<string>(TaskCreationOptions.RunContinuationsAsynchronously);
            string request = line;
            dispatcher.Enqueue(() => tcs.TrySetResult(BridgeMod.HandleRequest(request)));
            if (!tcs.Task.Wait(GameThreadTimeout))
            {
                Write(writer, Protocol.Error("game thread timeout", null));
                continue;
            }
            Write(writer, tcs.Task.Result);
        }
        BridgeMod.LogInfo("client disconnected");
    }

    private static void Write(StreamWriter writer, string payload)
    {
        try
        {
            writer.WriteLine(payload);
        }
        catch (Exception)
        {
            // client went away; the read loop will notice
        }
    }
}
