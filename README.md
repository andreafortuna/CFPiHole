
# CFPiHole

Simple python script, runnable from GHA, that allows importing PiHole domain blocking lists into Cloudflare Zero-Trust Gateway configuration.

### Usage

1. Create Cloudflare API token, from https://dash.cloudflare.com/profile/api-tokens, with 3 permissions `Account.Zero Trust : Edit` `Account.Account Firewall Access Rules : Edit` `Account.Access: Apps and Policies : Edit`
2. Get your Account ID from : https://dash.cloudflare.com/?to=/:account/workers
3. Clone this repository.
4. Configure action secrets: 
    * `CF_IDENTIFIER` with Account ID
    * `CF_API_TOKEN` with API Token
5. Modify `config.ini` with your preferred blocking lists
6. Enable action