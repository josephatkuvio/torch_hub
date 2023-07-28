namespace Torch.Web.Workflows;

public class Parameter
{
    public Parameter(int taskId, string name, string? value)
    {
        TaskId = taskId;
        Name = name;
        Value = value;
    }

    public int Id { get; private set; }
    public int TaskId { get; private set; }
    public TorchTask Task { get; private set; } = null!;
    public string Name { get; private set; }
    public string? Value { get; set; }

}

