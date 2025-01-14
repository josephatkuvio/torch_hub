﻿using Microsoft.AspNetCore.Components.Forms;
using Sparc.Blossom.Data;
using Torch.Web.Workflows;

namespace Torch.Web.Collections;

public class Specimen : Entity<int>
{
    private Specimen()
    {
        BatchId = "";
        Name = "";
        CreateDate = DateTime.UtcNow;
        InputFile = "";
        Status = "Created";
        StatusDate = DateTime.UtcNow;
    }
    
    public Specimen(int inputConnectionId, string batchId, string name, string inputFile) : this()
    {
        InputConnectionId = inputConnectionId;
        BatchId = batchId;
        Name = name;
        CreateDate = DateTime.UtcNow;
        InputFile = inputFile;
    }

    public Specimen(int inputConnectionId, string batchId, IBrowserFile file) : this()
    {
        InputConnectionId = inputConnectionId;
        BatchId = batchId;
        Name = file.Name;
        CreateDate = DateTime.UtcNow;
        InputFile = file.Name;
        File = file;
    }

    public int InputConnectionId { get; internal set; }
    public int? OutputConnectionId { get; set; }
    public string BatchId { get; private set; }
    public string InputFile { get; private set; }
    public string Name { get; private set; }
    public string? Status { get; private set; }
    public DateTime? StatusDate { get; private set; }
    public DateTime CreateDate { get; private set; }
    public DateTime? ProcessedDate { get; private set; }
    public string? Barcode { get; private set; }
    public string? CatalogNumber { get; private set; }
    public bool Deleted { get; private set; }
    public Connection InputConnection {  get; private set; } = null!;
    public Connection? OutputConnection { get; private set; }
    public List<SpecimenImage> Images { get; private set; } = new();
    public List<TorchTaskRun> TaskRuns { get; private set; } = new();
    public void Delete() => Deleted = true;

    public SpecimenImage? CardImage => 
        Images.OrderBy(x => x.Width ?? 1000000).FirstOrDefault() ?? 
        (InputFile.StartsWith("http") ? new SpecimenImage(Id, InputFile, "Original") : null);

    internal IBrowserFile? File { get; }

    public void SetInputFile(string name, string inputFile)
    {
        Name = name;
        InputFile = inputFile;
        StatusDate = DateTime.UtcNow;
        Status = "Uploaded";
    }
}

