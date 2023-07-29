using Microsoft.EntityFrameworkCore;
using Torch.Web.Collections;
using Torch.Web.Institutions;
using Torch.Web.Users;
using Torch.Web.Workflows;

namespace Torch.Web._Plugins;

public class TorchContext : DbContext
{
    public TorchContext(DbContextOptions<TorchContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder model)
    {
        model.Entity<Connection>().ToTable("connection");
        model.Entity<Identity>().ToTable("identity");
        model.Entity<Institution>().ToTable("institution");
        model.Entity<Specimen>().ToTable("specimen");
        model.Entity<SpecimenImage>().ToTable("specimenimage");
        model.Entity<TorchTask>().ToTable("task");
        model.Entity<TorchTaskRun>().ToTable("taskrun");
        model.Entity<User>().ToTable("user");
        model.Entity<Workflow>().ToTable("workflow");
        model.Entity<WorkflowUser>().ToTable("workflowuser").HasKey(x => new { x.WorkflowId, x.UserId });

        model.Entity<Specimen>().OwnsMany(x => x.Images);
        model.Entity<User>().Navigation(x => x.Roles).AutoInclude();
    }
}
