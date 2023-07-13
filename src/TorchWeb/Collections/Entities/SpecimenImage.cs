namespace Torch.Web.Collections;

public class SpecimenImage
{
    public SpecimenImage(int specimenId, string size)
    {
        SpecimenId = specimenId;
        Size = size;
        CreateDate = DateTime.UtcNow;
    }

    public int Id { get; private set; }
    public string Size { get; private set; }
    public int? Height { get; private set; }
    public int? Width { get; private set; }
    public string? Url { get; private set; }
    public DateTime CreateDate { get; private set; }
    public int SpecimenId { get; private set; }
    public Specimen Specimen { get; private set; } = null!;
    public string? ExternalUrl { get; private set; }
    public string? Hash_A { get; private set; }
    public string? Hash_B { get; private set; }
    public string? Hash_C { get; private set; }
    public string? Hash_D { get; private set; }
}