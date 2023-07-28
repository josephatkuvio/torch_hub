﻿using Microsoft.EntityFrameworkCore;
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
        model.Entity<Task>().UseTpcMappingStrategy();
        model.Entity<Parameter>().UseTpcMappingStrategy();
        
        model.Entity<Institution>().ToTable("institution");
        model.Entity<Collection>().ToTable("collection");
        model.Entity<Workflow>().ToTable("workflow");
        model.Entity<Collections.Specimen>().ToTable("specimen");
        model.Entity<SpecimenTask>().ToTable("specimen_tasks");
        model.Entity<SpecimenImage>().ToTable("specimenimage");
        model.Entity<User>().ToTable("user");
        model.Entity<Role>().ToTable("role");

        model.Entity<User>()
            .HasMany(x => x.Roles)
            .WithMany(x => x.Users)
            .UsingEntity("roles_users");

        model.Entity<Collections.Specimen>().Navigation(x => x.Images).AutoInclude();
    }
}
