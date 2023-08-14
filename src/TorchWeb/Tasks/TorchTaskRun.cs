using System.Text.Json;
using Torch.Web.Collections;

namespace Torch.Web.Workflows;

public class TorchTaskRun
{
    public int Id { get; set; }
    public int TaskId { get; set; }
    public int SpecimenId { get; set; }
    public Dictionary<string, string> Parameters { get; set; } = new();
    public DateTime StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public string? Status { get; set; }
    public string? Result { get; set; }
    public TorchTask Task { get; set; } = null!;
    public Specimen Specimen { get; set; } = null!;

    public JsonDocument? ResultJson()
    {
        if (Result == null) return null;
        try
        {
            return JsonDocument.Parse(Result);
        }
        catch (JsonException)
        {
            return null;
        }
    }

    public T? To<T>(string taskName)
    {
        var json = ResultJson();
        if (Task.Name != taskName || json == null) return default;

        try
        {
            return json.Deserialize<T>(new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
        }
        catch (JsonException)
        {
            return default;
        }
    }
}

