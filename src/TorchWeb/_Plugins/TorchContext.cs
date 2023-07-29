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
        model.Entity<TorchTask>();
        model.Entity<Parameter>();
        
        model.Entity<Institution>().ToTable("institution");
        model.Entity<WorkflowUser>().ToTable("workflowuser").HasKey(x => new { x.WorkflowId, x.UserId });
        model.Entity<Workflow>().ToTable("workflow");
        model.Entity<Specimen>().ToTable("specimen");
        model.Entity<SpecimenTask>().ToTable("specimentask");
        model.Entity<SpecimenImage>().ToTable("specimenimage");
        model.Entity<User>().ToTable("user");

        model.Entity<User>()
            .HasMany(x => x.Roles)
            .WithMany(x => x.Users)
            .UsingEntity("roles_users");

        model.Entity<Specimen>().Navigation(x => x.Images).AutoInclude();
        model.Entity<User>().Navigation(x => x.Roles).AutoInclude();
    }
}
