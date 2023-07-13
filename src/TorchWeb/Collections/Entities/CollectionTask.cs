using Torch.Web.Workflows;

namespace Torch.Web.Collections;

public class CollectionTask : TorchTask
{
    public CollectionTask(int collectionId, string funcName, string name, int sortOrder)
        : base(funcName, name, sortOrder)
    {
        CollectionId = collectionId;
    }

    public CollectionTask(int collectionId, TorchTask baseTask)
        : this(collectionId, baseTask.FuncName, baseTask.Name, baseTask.SortOrder)
    {
    }

    public int CollectionId { get; private set; }
    public Collection Collection { get; private set; } = null!;
    public List<TorchParameter> CollectionParameters { get; private set; } = new();
}