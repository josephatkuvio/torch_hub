using Torch.Web.Collections;

namespace Torch.Web.Workflows.Connections;

public class SFTPConnection : Connection
{
    public SFTPConnection(int workflowId, string direction, string name, string host)
        : base(workflowId, nameof(SFTPConnection), direction, name, host)
    {
    }

    public SFTPConnection(Workflow workflow, string direction, string name, string host)
        : this(workflow.Id, direction, name, host)
    {
        Workflow = workflow;
    }

    internal override Task<Specimen> UploadAsync(Specimen specimen, Stream stream)
    {
        throw new NotImplementedException();
    }
}
