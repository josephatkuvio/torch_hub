using Sparc.Blossom.Data;

namespace Torch.Web.Collections;

public class Specimen : Entity<int>
{
    public Specimen(int collectionId, string name)
    {
        CollectionId = collectionId;
        Name = name;
        CreateDate = DateTime.UtcNow;
    }

    public int CollectionId { get; private set; }
    public int? WorkflowId { get; private set; }
    public string Name { get; private set; }
    public DateTime CreateDate { get; private set; }
    public string? UploadPath { get; private set; }
    public string? Barcode { get; private set; }
    public string? CatalogNumber { get; private set; }
    public string? BatchId { get; private set; }
    public int Deleted { get; private set; }
    public int HasDng { get; private set; }
    public List<SpecimenImage> Images { get; private set; } = new();
    public List<SpecimenTask> Tasks { get; private set; } = new();
    public Collection Collection { get; private set; } = null!;
    public void Delete() => Deleted = 1;

    public SpecimenImage? CardImage => Images.OrderBy(x => x.Width ?? 1000000).FirstOrDefault();
}

