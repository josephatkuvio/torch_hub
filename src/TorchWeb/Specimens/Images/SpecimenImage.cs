namespace Torch.Web.Collections;

public class SpecimenImage
{
    public SpecimenImage(int specimenId, string outputFile, string size)
    {
        SpecimenId = specimenId;
        OutputFile = outputFile;
        Size = size;
        CreateDate = DateTime.UtcNow;
    }

    public int Id { get; private set; }
    public int SpecimenId { get; private set; }
    public string OutputFile { get; private set; }
    public string? Url { get; private set; }
    public string Size { get; private set; }
    public int? Height { get; private set; }
    public int? Width { get; private set; }
    public DateTime CreateDate { get; private set; }
    public Specimen Specimen { get; private set; } = null!;
    public string? HashA { get; private set; }
    public string? HashB { get; private set; }
    public string? HashC { get; private set; }
    public string? HashD { get; private set; }

    public string? AbsoluteUrl(string? baseUrl) =>
        (OutputFile.StartsWith("http") ? "" : baseUrl)
        + OutputFile;
}