namespace Torch.Web.Collections;

public class CollectionTask
{
    public CollectionTask(int collectionId, string funcName, string name, int sortOrder)
    {
        CollectionId = collectionId;
        FuncName = funcName;
        Name = name;
    }

    public int Id { get; private set; }
    public int CollectionId { get; private set; }
    public string FuncName { get; private set; }
    public string Name { get; private set; }
    public int SortOrder { get; private set; }
    public string? Description { get; private set; }
    public Collection Collection { get; private set; } = null!;
    public List<CollectionTaskParameter> Parameters { get; private set; } = new();
}