using Auth0.AspNetCore.Authentication;
using Blazored.Modal;
using Microsoft.EntityFrameworkCore;
using Sparc.Blossom.Data;
using Torch.Web._Plugins;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddBlazoredModal();

builder.Services.AddDbContext<TorchContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Database"))
                                           .UseSnakeCaseNamingConvention());

builder.Services.AddScoped<DbContext, TorchContext>();
builder.Services.AddScoped(typeof(IRepository<>), typeof(SqlServerRepository<>));
builder.Services.AddScoped<TorchAuthenticator>();
builder.Services.AddAuth0WebAppAuthentication(options =>
{
    options.Domain = builder.Configuration["Auth0:Domain"]!;
    options.ClientId = builder.Configuration["Auth0:ClientId"]!;
    options.ClientSecret = builder.Configuration["Auth0:ClientSecret"]!;
});
//builder.Services.AddBlossom<TorchApi>(builder.Configuration);

var app = builder.Build();

if (!app.Environment.IsDevelopment())
    app.UseHsts();

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();

app.MapRazorPages();
app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();