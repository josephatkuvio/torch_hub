using Torch.Web.Collections;

namespace Torch.Web.Workflows;

public class Connection
{
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
    public List<Specimen> InputSpecimens { get; set; } = new();
    public List<Specimen> OutputSpecimens { get; set; } = new();
}
