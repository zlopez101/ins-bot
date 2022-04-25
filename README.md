# Ins-bot

This is a microsoft teams bot built for handling insurance verification workflows that are commonly requested from clinics. These tasks are often repetitive, and involve simple lookups on previously gathered information that a bot should be able to reference without human supervision. Give me a try [here]()!

## How does the bot work?

The bot is running in an Azure Python Web App. The app has /api/messages endpoint that the bot posts to. From there, the DialogBot(ActivityHandler) class manages a dialog workflow that from a MainDialog Class. The class holds references to the implemented workflows that access the same user state and help/cancel/agent methods through a BaseDialog class. The I take the end-user'a (typically a PAR, MA, or RN) provided info and perform simple lookups on an airtable API.

## Who are my customers?

End-users would be PAR, MA, RN, or other clinic staff handling insurance-related tasks.

##

## Deploy the bot to Azure if your name is Zach

To learn more about deploying a bot to Azure, see [Deploy your bot to Azure](https://aka.ms/azuredeployment) for a complete list of deployment instructions.

### Provision the bot resources

0. Configure Virtual Environment

   - only started these notes _after_ installing `pytest-aiohttp`
   - use `botbuilder 4.14.2`
   - those modules require that 3.6.2 < `aiohttp` < 3.8.0
   - but `pytest-aiohttp` wants 3.8.1 - something to keep in mind
   - still seems to be working locally for dev purposes

1. az ad app create --display-name "ins-verification-bot" --password "<password>" --available-to-other-tenant

   - appId: <appId>
   - password: <password>

2. az deployment sub create --template-file ""C:\Users\zachl\Codes\test-azure-deployment\my_chat_bot\deploymentTemplates\template-with-new-rg.json"" --location eastus --parameters appId="<appId>" appSecret="<password>" botId="ut-ins-bot-production" botSku=F0 newAppServicePlanName="ut-ins-bot-app-service" newWebAppName="ut-ins-bot-web-app" groupName="ut-ins-bot-app" groupLocation="eastus" newAppServicePlanLocation="eastus" newAppServicePlanSku=F0 --name "ut-ins-bot-production"

   - multi tenant appType causes command to fail
   - using the other test deployment template b/c might have messed this one up
   - also add the AppPlanSku as F0 -> delete this actually

3. Release the actual build

## Further reading

- [Bot Framework Documentation](https://docs.botframework.com)
- [Bot Basics](https://docs.microsoft.com/azure/bot-service/bot-builder-basics?view=azure-bot-service-4.0)
- [Dialogs](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-dialog?view=azure-bot-service-4.0)
- [Gathering Input Using Prompts](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-prompts?view=azure-bot-service-4.0&tabs=csharp)
- [Activity processing](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-activity-processing?view=azure-bot-service-4.0)
- [Azure Bot Service Introduction](https://docs.microsoft.com/azure/bot-service/bot-service-overview-introduction?view=azure-bot-service-4.0)
- [Azure Bot Service Documentation](https://docs.microsoft.com/azure/bot-service/?view=azure-bot-service-4.0)
- [Azure CLI](https://docs.microsoft.com/cli/azure/?view=azure-cli-latest)
- [Azure Portal](https://portal.azure.com)
- [Channels and Bot Connector Service](https://docs.microsoft.com/en-us/azure/bot-service/bot-concepts?view=azure-bot-service-4.0)
