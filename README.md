Add variables secrets to 
`https://github.com/your-user/your-repository/settings/secrets/actions`:

* `CF_IDENTIFIER` from your Account ID from : https://dash.cloudflare.com/?to=/:account/workers

* `CF_API_TOKEN` take from : https://dash.cloudflare.com/profile/api-tokens with 3 permissions `Account.Zero Trust : Edit` `Account.Account Firewall Access Rules : Edit` `Account.Access: Apps and Policies : Edit`

or add to  [.env](.env)