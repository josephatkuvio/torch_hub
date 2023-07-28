namespace Torch.Web.Workflows;

public class TorchTask
{
    public TorchTask(int workflowId, string funcName, string name)
    {
        WorkflowId = workflowId;
        FuncName = funcName;
        Name = name;
    }

    public int Id { get; private set; }
    public int WorkflowId { get; private set; }
    public Workflow Workflow { get; private set; } = null!;
    public string FuncName { get; private set; }
    public string Name { get; private set; }
    public int? SortOrder { get; private set; }
    public string? Description { get; private set; }
    public List<Parameter> Parameters { get; private set; } = new();
}