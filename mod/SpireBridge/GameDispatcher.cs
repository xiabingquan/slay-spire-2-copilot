using System;
using System.Collections.Concurrent;
using Godot;

namespace MimoSpire.Bridge;

// Main-thread pump: background socket threads enqueue work here; _Process
// drains at most MaxPerFrame items per frame. Game objects are only ever
// touched inside drained work items.
public partial class GameDispatcher : Node
{
    private const int MaxPerFrame = 32;
    private readonly ConcurrentQueue<Action> _queue = new();

    public static GameDispatcher? Instance { get; private set; }

    public override void _Ready()
    {
        Instance = this;
        Name = "SpireBridgeDispatcher";
        BridgeMod.LogInfo("dispatcher ready");
    }

    public override void _ExitTree()
    {
        if (Instance == this)
        {
            Instance = null;
        }
    }

    public void Enqueue(Action work) => _queue.Enqueue(work);

    public override void _Process(double delta)
    {
        for (int i = 0; i < MaxPerFrame && _queue.TryDequeue(out Action? work); i++)
        {
            try
            {
                work();
            }
            catch (Exception e)
            {
                BridgeMod.LogErr($"dispatcher work failed: {e}");
            }
        }
    }
}
