namespace Torch.Web.Workflows;

public abstract class TorchTask
{
    public TorchTask(string funcName, string name, int sortOrder)
    {
        FuncName = funcName;
        Name = name;
        SortOrder = sortOrder;
    }
    
    public int Id { get; private set; }
    public string FuncName { get; private set; }
    public string Name { get; private set; }
    public int SortOrder { get; private set; }
    public string? Description { get; private set; }
    public List<TorchParameter> Parameters { get; private set; } = new();
}

public abstract class TorchParameter
{
    public TorchParameter(string name, string value)
    {
        Name = name;
        Value = value;
    }

    public int Id { get; private set; }
    public string Name { get; private set; }
    public string Value { get; internal set; }
}