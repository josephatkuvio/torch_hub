using Blazored.Modal;
using Microsoft.EntityFrameworkCore;
using Sparc.Blossom;
using Torch.Web._Plugins;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddBlazoredModal();
builder.Services.AddDbContext<TorchContext>(options => 
    options.UseNpgsql(builder.Configuration.GetConnectionString("Database"))
           .UseSnakeCaseNamingConvention());
//builder.Services.AddBlossom<TorchApi>(builder.Configuration);

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();

app.UseStaticFiles();

app.UseRouting();

app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();

await builder.Build().RunAsync();
