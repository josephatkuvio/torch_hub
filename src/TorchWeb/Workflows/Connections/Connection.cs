using Torch.Web.Collections;

namespace Torch.Web.Workflows;

public abstract class Connection
{
    public Connection(int workflowId, string containerType, string direction, string name, string host)
    {
        WorkflowId = workflowId;
        ContainerType = containerType;
        Direction = direction;
        Name = name;
        Host = host;
    }

    public int Id { get; set; }
    public int WorkflowId { get; set; }
    public string Direction { get; set; }

    public string Name { get; set; }
    public string? Description {  get; set; }
    public string ContainerType {  get; set; }
    public string Host {  get; set; }
    public string? UserId { get; set; }
    public string? PasswordKey { get; set; }
    public string? ApplicationId { get; set; }
    public string? ApplicationKey { get; set; }
    public Workflow Workflow { get; set; } = null!;
    public List<Specimen> Specimens { get; set; } = new();

    internal virtual Task<bool> InitializeAsync()
    {
        return Task.FromResult(false);
    }

    internal virtual Task<IEnumerable<Specimen>> GetSpecimensAsync(int take = 50, string? continuationToken = null)
    {
        return Task.FromResult(Enumerable.Empty<Specimen>());
    }

    internal virtual Task<Specimen> UploadSpecimenAsync(string fileName, Stream stream)
    {
        throw new NotImplementedException();
    }
}
