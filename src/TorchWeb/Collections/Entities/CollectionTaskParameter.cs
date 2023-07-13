namespace Torch.Web.Collections;

public class CollectionTaskParameter
{
    public CollectionTaskParameter(int collectionTaskId, string name, string value)
    {
        CollectionTaskId = collectionTaskId;
        Name = name;
        Value = value;
    }
    public int Id { get; private set; }
    public int CollectionTaskId { get; private set; }
    public string Name { get; private set; }
    public string Value { get; private set; }
    public CollectionTask Task { get; private set; } = null!;
}