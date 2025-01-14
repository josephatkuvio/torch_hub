﻿using Microsoft.EntityFrameworkCore;
using Torch.Web.Collections;
using Torch.Web.Institutions;
using Torch.Web.Users;
using Torch.Web.Workflows;
using Torch.Web.Workflows.Connections;

namespace Torch.Web._Plugins;

public class TorchContext : DbContext
{
    public TorchContext(DbContextOptions<TorchContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder model)
    {
        model.Entity<Connection>().ToTable("connection").HasDiscriminator(x => x.ContainerType);
        model.Entity<Connection>().HasQueryFilter(x => x.DeletedDate == null);
        model.Entity<AzureBlobConnection>();
        model.Entity<AmazonS3Connection>();
        model.Entity<SFTPConnection>();

        model.Entity<Institution>().ToTable("institution");
        model.Entity<Specimen>().ToTable("specimen");
        model.Entity<TorchTask>().ToTable("task");
        model.Entity<TorchTaskRun>().ToTable("taskrun");
        model.Entity<User>().ToTable("user");
        model.Entity<Workflow>().ToTable("workflow");
        model.Entity<Workflow>().Navigation(x => x.Connections).AutoInclude();
        model.Entity<Workflow>().Navigation(x => x.Tasks).AutoInclude();

        model.Entity<WorkflowUser>().ToTable("workflowuser").HasKey(x => new { x.WorkflowId, x.UserId });

        model.Entity<Specimen>().OwnsMany(x => x.Images).ToTable("specimenimage");
        model.Entity<Specimen>().HasOne(x => x.InputConnection).WithMany(x => x.Specimens).HasForeignKey(x => x.InputConnectionId);
        model.Entity<Specimen>().HasOne(x => x.OutputConnection).WithMany().HasForeignKey(x => x.OutputConnectionId);

        model.Entity<User>().HasOne(x => x.CurrentWorkflow).WithMany().HasForeignKey(x => x.CurrentWorkflowId);
        model.Entity<Institution>().HasOne(x => x.Owner).WithMany().HasForeignKey(x => x.OwnerId);

        model.Entity<User>().OwnsMany(x => x.Identities).ToTable("identity");

        // Json support
        model.Entity<TorchTask>().Property(x => x.Parameters).HasColumnType("jsonb");
        model.Entity<TorchTaskRun>().Property(x => x.Parameters).HasColumnType("jsonb");

        // Connection inheritance
        model.Entity<AzureBlobConnection>();

    }
}
