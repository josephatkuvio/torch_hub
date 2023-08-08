using System.Text.Json;
using Torch.Web.Collections;

namespace Torch.Web.Workflows;

public class TorchTaskRun : IDisposable
{
    public int Id { get; set; }
    public int TaskId { get; set; }
    public int SpecimenId { get; set; }
    public Dictionary<string, string> Parameters { get; set; } = new();
    public DateTime StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string? Status { get; set; }
    public JsonDocument? Result { get; set; }
    public TorchTask Task { get; set; } = null!;
    public Specimen Specimen { get; set; } = null!;

    public List<T?>? To<T>(string taskName)
        => Task.Name == taskName && Result != null
            ? Result.Deserialize<List<T?>>()
            : new();

    public void Dispose() => Result?.Dispose();
}

