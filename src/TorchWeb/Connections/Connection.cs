using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Microsoft.AspNetCore.Http.Connections.Client;
using System;
using Torch.Web.Collections;
using Torch.Web.Workflows.Connections;

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
    public string Host { get; set; }
    public string? UserId { get; set; }
    public string? PasswordKey { get; set; }
    public string? ApplicationId { get; set; }
    public string? ApplicationKey { get; set; }
    public DateTime? CreatedDate { get; set; }
    public DateTime? DeletedDate { get; set; }
    public Workflow Workflow { get; set; } = null!;
    public List<Specimen> Specimens { get; set; } = new();
    private SecretClient? Client { get; set; }

    internal virtual Task<bool> InitializeAsync()
    {
        return Task.FromResult(false);
    }

    internal virtual Task<IEnumerable<Specimen>> GetAsync(int take = 50, string? continuationToken = null)
    {
        return Task.FromResult(Enumerable.Empty<Specimen>());
    }

    internal async Task SetPasswordAsync(string password)
    {
        PasswordKey ??= RandomString(64);
        Client ??= new SecretClient(new Uri("https://torchhub.vault.azure.net"), new DefaultAzureCredential());
        await Client.SetSecretAsync(PasswordKey, password);
    }

    internal abstract Task<Specimen> UploadAsync(Specimen specimen, Stream stream);

    private static readonly Random random = new();
    public static string RandomString(int length)
    {
        const string chars = "abcdefghijklmnopqrstuvwxyz0123456789";
        return new string(Enumerable.Repeat(chars, length)
            .Select(s => s[random.Next(s.Length)]).ToArray());
    }

    internal static Connection Create(string containerType, int workflowId, string direction, string name, string host)
    {
        return containerType switch
        {
            "AzureBlobConnection" => new AzureBlobConnection(workflowId, direction, name, host),
            "AmazonS3Connection" => new AmazonS3Connection(workflowId, direction, name, host),
            "SFTPConnection" => new SFTPConnection(workflowId, direction, name, host),
            _ => throw new NotSupportedException(),
        };
    }

    internal Connection ChangeContainerType(string containerType)
    {
        DeletedDate = DateTime.UtcNow;
        var newConnection = Create(containerType, WorkflowId, Direction, Name, Host);
        newConnection.UserId = UserId;
        newConnection.ApplicationId = ApplicationId;

        return newConnection;
    }
}
