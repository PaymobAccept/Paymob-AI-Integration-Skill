# Paymob — Ruby / Rails

Clean, correct reference (Intention API + Unified Checkout + HMAC-verified webhook). Read `intention-api.md` and `hmac-verification.md` alongside this.

## Environment

```env
PAYMOB_BASE_URL=https://accept.paymob.com
PAYMOB_SECRET_KEY=sk_test_xxxxxxxx
PAYMOB_PUBLIC_KEY=pk_test_xxxxxxxx
PAYMOB_HMAC_SECRET=your_hmac_secret
PAYMOB_INTEGRATION_ID_CARD=123456
APP_URL=https://yoursite.com
```

## Client (`lib/paymob.rb`) — net/http, no gems required

```ruby
require "net/http"
require "json"
require "openssl"
require "uri"

class Paymob
  def initialize
    @base   = (ENV["PAYMOB_BASE_URL"] || "https://accept.paymob.com").chomp("/")
    @secret = ENV.fetch("PAYMOB_SECRET_KEY")
    @public = ENV.fetch("PAYMOB_PUBLIC_KEY")
    @hmac   = ENV.fetch("PAYMOB_HMAC_SECRET")
  end

  def create_intention(amount_cents:, currency:, payment_methods:, special_reference:, customer:, items: [])
    payload = {
      amount: amount_cents,
      currency: currency,
      payment_methods: payment_methods,
      items: items,
      special_reference: special_reference,
      billing_data: {
        first_name: customer[:first_name], last_name: customer[:last_name],
        email: customer[:email], phone_number: customer[:phone], # REQUIRED
        apartment: "NA", floor: "NA", street: "NA", building: "NA",
        shipping_method: "NA", postal_code: "NA", city: "NA", state: "NA", country: "EGY"
      },
      customer: { first_name: customer[:first_name], last_name: customer[:last_name], email: customer[:email] },
      notification_url: "#{ENV['APP_URL']}/api/paymob/webhook",
      redirection_url: "#{ENV['APP_URL']}/payment/complete"
    }
    res = post("/v1/intention/", payload)
    { id: res["id"], client_secret: res["client_secret"] }
  end

  def checkout_url(client_secret)
    "#{@base}/unifiedcheckout/?publicKey=#{@public}&clientSecret=#{client_secret}"
  end

  def verify_transaction_post_hmac(obj, received_hmac)
    fields = [
      obj["amount_cents"], obj["created_at"], obj["currency"], obj["error_occured"],
      obj["has_parent_transaction"], obj["id"], obj["integration_id"], obj["is_3d_secure"],
      obj["is_auth"], obj["is_capture"], obj["is_refunded"], obj["is_standalone_payment"],
      obj["is_voided"], obj.dig("order", "id"), obj["owner"], obj["pending"],
      obj.dig("source_data", "pan"), obj.dig("source_data", "sub_type"),
      obj.dig("source_data", "type"), obj["success"]
    ]
    concat   = fields.map { |v| bool_str(v) }.join
    computed = OpenSSL::HMAC.hexdigest("SHA512", @hmac, concat)
    # timing-safe
    return false unless computed.bytesize == received_hmac.to_s.bytesize
    OpenSSL.fixed_length_secure_compare(computed, received_hmac.to_s)
  end

  def refund(transaction_id, amount_cents)
    post("/api/acceptance/void_refund/refund", transaction_id: transaction_id, amount_cents: amount_cents)
  end

  def void(transaction_id)
    post("/api/acceptance/void_refund/void", transaction_id: transaction_id)
  end

  def capture(transaction_id, amount_cents)
    post("/api/acceptance/capture", transaction_id: transaction_id, amount_cents: amount_cents)
  end

  private

  # Ruby's true.to_s is "true" already — but be explicit to avoid surprises with nil.
  def bool_str(v)
    return "true" if v == true
    return "false" if v == false
    v.to_s
  end

  def post(path, body)
    uri = URI("#{@base}#{path}")
    http = Net::HTTP.new(uri.host, uri.port); http.use_ssl = (uri.scheme == "https")
    req = Net::HTTP::Post.new(uri)
    req["Authorization"] = "Token #{@secret}"   # literal "Token", not "Bearer"
    req["Content-Type"]  = "application/json"
    req.body = body.to_json
    res = http.request(req)
    raise "Paymob error #{res.code}: #{res.body}" if res.code.to_i >= 400
    JSON.parse(res.body)
  end
end
```

## Rails controller

```ruby
# config/routes.rb
#   post "/api/checkout",        to: "payments#checkout"
#   post "/api/paymob/webhook",  to: "payments#webhook"

class PaymentsController < ApplicationController
  skip_before_action :verify_authenticity_token, only: [:webhook, :checkout]

  def checkout
    paymob = Paymob.new
    intention = paymob.create_intention(
      amount_cents: (params[:amount].to_f * 100).round,
      currency: "EGP",
      payment_methods: [ENV["PAYMOB_INTEGRATION_ID_CARD"].to_i],
      special_reference: params[:order_id].to_s,
      customer: { first_name: params[:first_name] || "NA", last_name: params[:last_name] || "NA",
                  email: params[:email], phone: params[:phone] },
      items: []
    )
    render json: { checkout_url: paymob.checkout_url(intention[:client_secret]) }
  end

  def webhook
    paymob   = Paymob.new
    obj      = params[:obj] || {}
    received = params[:hmac].to_s
    unless paymob.verify_transaction_post_hmac(obj.as_json, received)
      return render json: { error: "Invalid HMAC" }, status: :unauthorized
    end
    if obj["success"] && !obj["pending"]
      # mark_order_paid(obj.dig("order", "id")) idempotently, then fulfill
    end
    render json: { received: true }
  end
end
```

## Gotchas

- Header `Authorization: Token <secret>` (not Bearer). Amount in **cents**. `phone_number` required.
- Booleans concatenate as `true`/`false` (Ruby's `to_s` already does this; `bool_str` guards `nil`).
- Use `OpenSSL.fixed_length_secure_compare` (timing-safe). Verify HMAC before trusting `success`; never trust redirect params. `client_secret` is single-use.
