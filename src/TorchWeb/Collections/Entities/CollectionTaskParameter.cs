using Torch.Web.Workflows;

namespace Torch.Web.Collections;

public class CollectionTaskParameter : TorchParameter
{
    public CollectionTaskParameter(int collectionTaskId, string name, string value)
        : base(name, value)
    {
        CollectionTaskId = collectionTaskId;
    }
    public int CollectionTaskId { get; private set; }
    public CollectionTask Task { get; private set; } = null!;
}