using Microsoft.EntityFrameworkCore;
using Torch.Web.Collections;
using Torch.Web.Institutions;
using Torch.Web.Users;

namespace Torch.Web._Plugins;

public class TorchContext : DbContext
{
    public TorchContext(DbContextOptions<TorchContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder model)
    {
        model.Entity<Institution>().ToTable("institution");
        model.Entity<Collection>().ToTable("collection");
        model.Entity<CollectionTask>().ToTable("collection_tasks");
        model.Entity<CollectionTaskParameter>().ToTable("collection_tasks_parameters");
        model.Entity<Specimen>().ToTable("specimen");
        model.Entity<SpecimenTask>().ToTable("specimen_tasks");
        model.Entity<SpecimenTaskParameter>().ToTable("specimen_tasks_parameters");
        model.Entity<SpecimenImage>().ToTable("specimenimage");
        model.Entity<User>().ToTable("user");
        model.Entity<Role>().ToTable("role");

        model.Entity<User>()
            .HasMany(x => x.Roles)
            .WithMany(x => x.Users)
            .UsingEntity("roles_users");
    }
}
