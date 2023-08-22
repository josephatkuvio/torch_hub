using Torch.Web.Collections;

namespace Torch.Web.Workflows.Connections;

public class AmazonS3Connection : Connection
{
    public AmazonS3Connection(int workflowId, string direction, string name, string host)
        : base(workflowId, nameof(AmazonS3Connection), direction, name, host)
    {
    }

    public AmazonS3Connection(Workflow workflow, string direction, string name, string host)
        : this(workflow.Id, direction, name, host)
    {
        Workflow = workflow;
    }

    internal override Task<Specimen> UploadAsync(Specimen specimen, Stream stream)
    {
        throw new NotImplementedException();
    }
}
