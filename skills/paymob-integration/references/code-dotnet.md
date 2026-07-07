# Paymob — .NET / C# (ASP.NET Core)

Clean, correct reference (Intention API + Unified Checkout + HMAC-verified webhook). Read `intention-api.md` and `hmac-verification.md` alongside this.

## Configuration (`appsettings.json` / env)

```json
{
  "Paymob": {
    "BaseUrl": "https://accept.paymob.com",
    "SecretKey": "sk_test_xxxxxxxx",
    "PublicKey": "pk_test_xxxxxxxx",
    "HmacSecret": "your_hmac_secret",
    "IntegrationIdCard": 123456,
    "AppUrl": "https://yoursite.com"
  }
}
```

## Service (`PaymobService.cs`)

```csharp
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

public class PaymobOptions
{
    public string BaseUrl { get; set; } = "https://accept.paymob.com";
    public string SecretKey { get; set; } = "";
    public string PublicKey { get; set; } = "";
    public string HmacSecret { get; set; } = "";
    public int IntegrationIdCard { get; set; }
    public string AppUrl { get; set; } = "";
}

public record CustomerInfo(string FirstName, string LastName, string Email, string Phone);

public class PaymobService
{
    private readonly HttpClient _http;
    private readonly PaymobOptions _o;

    public PaymobService(HttpClient http, PaymobOptions options)
    {
        _o = options;
        _http = http;
        _http.BaseAddress = new Uri(_o.BaseUrl.TrimEnd('/') + "/");
        // literal scheme "Token", not "Bearer"
        _http.DefaultRequestHeaders.Add("Authorization", $"Token {_o.SecretKey}");
    }

    public async Task<(long Id, string ClientSecret)> CreateIntentionAsync(
        long amountCents, string currency, int[] paymentMethods,
        string specialReference, CustomerInfo c)
    {
        var payload = new
        {
            amount = amountCents,
            currency,
            payment_methods = paymentMethods,
            items = Array.Empty<object>(),
            special_reference = specialReference,
            billing_data = new
            {
                first_name = c.FirstName, last_name = c.LastName, email = c.Email,
                phone_number = c.Phone,                 // REQUIRED
                apartment = "NA", floor = "NA", street = "NA", building = "NA",
                shipping_method = "NA", postal_code = "NA", city = "NA",
                state = "NA", country = "EGY"
            },
            customer = new { first_name = c.FirstName, last_name = c.LastName, email = c.Email },
            notification_url = $"{_o.AppUrl}/api/paymob/webhook",
            redirection_url = $"{_o.AppUrl}/payment/complete"
        };

        var resp = await _http.PostAsJsonAsync("v1/intention/", payload);
        resp.EnsureSuccessStatusCode();
        using var doc = JsonDocument.Parse(await resp.Content.ReadAsStringAsync());
        var root = doc.RootElement;
        return (root.GetProperty("id").GetInt64(),
                root.GetProperty("client_secret").GetString()!);
    }

    public string CheckoutUrl(string clientSecret) =>
        $"{_o.BaseUrl.TrimEnd('/')}/unifiedcheckout/?publicKey={_o.PublicKey}&clientSecret={clientSecret}";

    // Transaction HMAC for the POST webhook. `obj` is the parsed body.obj element.
    public bool VerifyTransactionPostHmac(JsonElement obj, string receivedHmac)
    {
        string[] fields =
        {
            Raw(obj, "amount_cents"), Raw(obj, "created_at"), Raw(obj, "currency"),
            Raw(obj, "error_occured"), Raw(obj, "has_parent_transaction"), Raw(obj, "id"),
            Raw(obj, "integration_id"), Raw(obj, "is_3d_secure"), Raw(obj, "is_auth"),
            Raw(obj, "is_capture"), Raw(obj, "is_refunded"), Raw(obj, "is_standalone_payment"),
            Raw(obj, "is_voided"), Raw(obj.GetProperty("order"), "id"), Raw(obj, "owner"),
            Raw(obj, "pending"), Raw(obj.GetProperty("source_data"), "pan"),
            Raw(obj.GetProperty("source_data"), "sub_type"),
            Raw(obj.GetProperty("source_data"), "type"), Raw(obj, "success")
        };
        var concat = string.Concat(fields);
        using var h = new HMACSHA512(Encoding.UTF8.GetBytes(_o.HmacSecret));
        var computed = Convert.ToHexString(h.ComputeHash(Encoding.UTF8.GetBytes(concat))).ToLowerInvariant();
        return CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(computed), Encoding.UTF8.GetBytes(receivedHmac ?? ""));
    }

    // Emit each value exactly as it appears in JSON: booleans as true/false, numbers unquoted, strings raw.
    private static string Raw(JsonElement parent, string name)
    {
        var el = parent.GetProperty(name);
        return el.ValueKind switch
        {
            JsonValueKind.True => "true",
            JsonValueKind.False => "false",
            JsonValueKind.String => el.GetString() ?? "",
            _ => el.GetRawText()
        };
    }

    public Task<HttpResponseMessage> Refund(long txnId, long amountCents) =>
        _http.PostAsJsonAsync("api/acceptance/void_refund/refund",
            new { transaction_id = txnId, amount_cents = amountCents });
    public Task<HttpResponseMessage> Void(long txnId) =>
        _http.PostAsJsonAsync("api/acceptance/void_refund/void", new { transaction_id = txnId });
    public Task<HttpResponseMessage> Capture(long txnId, long amountCents) =>
        _http.PostAsJsonAsync("api/acceptance/capture",
            new { transaction_id = txnId, amount_cents = amountCents });
}
```

> **Boolean handling:** the `Raw` helper emits `true`/`false` (not `True`/`False`) and unquoted numbers, matching exactly what Paymob concatenated to produce the HMAC.

## Minimal-API endpoints (`Program.cs`)

```csharp
app.MapPost("/api/checkout", async (CheckoutDto dto, PaymobService paymob, PaymobOptions o) =>
{
    var (_, clientSecret) = await paymob.CreateIntentionAsync(
        amountCents: (long)Math.Round(dto.Amount * 100),
        currency: "EGP",
        paymentMethods: new[] { o.IntegrationIdCard },
        specialReference: dto.OrderId,
        c: new CustomerInfo(dto.FirstName, dto.LastName, dto.Email, dto.Phone));
    return Results.Ok(new { checkoutUrl = paymob.CheckoutUrl(clientSecret) });
});

app.MapPost("/api/paymob/webhook", async (HttpRequest req, PaymobService paymob) =>
{
    using var doc = await JsonDocument.ParseAsync(req.Body);
    if (!doc.RootElement.TryGetProperty("obj", out var obj))
        return Results.Json(new { error = "no obj" }, statusCode: 400);

    var received = req.Query["hmac"].ToString();
    if (!paymob.VerifyTransactionPostHmac(obj, received))
        return Results.Json(new { error = "Invalid HMAC" }, statusCode: 401);

    if (obj.GetProperty("success").GetBoolean() && !obj.GetProperty("pending").GetBoolean())
    {
        // MarkOrderPaid(obj.GetProperty("order").GetProperty("id")) idempotently, then fulfill
    }
    return Results.Ok(new { received = true });
});

record CheckoutDto(decimal Amount, string OrderId, string FirstName, string LastName, string Email, string Phone);
```

Register in DI: `builder.Services.AddSingleton(paymobOptions); builder.Services.AddHttpClient<PaymobService>();`

## Gotchas

- Header scheme is `Token` (not `Bearer`). Amount in **cents**. `phone_number` required.
- Concatenate booleans as lowercase `true`/`false` (the `Raw` helper does this).
- Use `CryptographicOperations.FixedTimeEquals` (timing-safe). Verify HMAC before trusting `success`; never trust redirect params. `client_secret` is single-use.
