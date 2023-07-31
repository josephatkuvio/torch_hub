using Sparc.Blossom.Data;
using Torch.Web.Workflows;

namespace Torch.Web.Collections;

public class Specimen : Entity<int>
{
    private Specimen()
    { }
    
    public Specimen(int inputConnectionId, string name, string inputFile)
    {
        InputConnectionId = inputConnectionId;
        Name = name;
        CreateDate = DateTime.UtcNow;
        InputFile = inputFile;
    }

    public int InputConnectionId { get; }
    public int? OutputConnectionId { get; set; }
    public string InputFile { get; }
    public string Name { get; private set; }
    public DateTime CreateDate { get; private set; }
    public string? Barcode { get; private set; }
    public string? CatalogNumber { get; private set; }
    public int Deleted { get; private set; }
    public Connection InputConnection {  get; private set; } = null!;
    public Connection? OutputConnection { get; private set; }
    public List<SpecimenImage> Images { get; private set; } = new();
    public List<TorchTaskRun> TaskRuns { get; private set; } = new();
    public void Delete() => Deleted = 1;

    public SpecimenImage? CardImage => Images.OrderBy(x => x.Width ?? 1000000).FirstOrDefault();
}

