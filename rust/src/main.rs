mod nicknamer;

use poise::serenity_prelude as serenity;

struct Data {} // User data, which is stored and accessible in all command invocations
type Error = Box<dyn std::error::Error + Send + Sync>;
type Context<'a> = poise::Context<'a, Data, Error>;

/// Ping command to test bot availability \
/// Any instance of bot connected to the server will respond with "Pong!" and some \
///     runtime information.
#[poise::command(prefix_command)]
async fn ping(ctx: Context<'_>) -> Result<(), Error> {
    ctx.reply("pong").await?;
    Ok(())
}

/// Routine responsible for 'nick' discord command.
///    This function handles the 'nick' command for the `nicknamer` bot. Its purpose is to \
///     allow discord users to manage each other's nicknames, even if they are in the same \
///     Discord Role. The bot applies any nickname changes as specified by this command. \
///     This command assumes that the bot has a higher Role than all users which invoke this \
///     command. \
///     In certain failure scenarios, such as offering an invalid nickname, the bot will \
///     reply with information about the invalid command.
#[poise::command(prefix_command)]
async fn nick(ctx: Context<'_>, member: serenity::Member) -> Result<(), Error> {
    nicknamer::nick(member.user.id);
    Ok(())
}

#[tokio::main]
async fn main() {
    let token = std::env::var("DISCORD_TOKEN").expect("missing DISCORD_TOKEN");
    let intents = serenity::GatewayIntents::non_privileged();

    let framework = poise::Framework::<Data, Error>::builder()
        .options(poise::FrameworkOptions {
            commands: vec![],
            prefix_options: poise::PrefixFrameworkOptions {
                prefix: Some("!".into()),
                ..Default::default()
            },
            ..Default::default()
        })
        .setup(|ctx, _ready, framework| {
            Box::pin(async move {
                poise::builtins::register_globally(ctx, &framework.options().commands).await?;
                Ok(Data {})
            })
        })
        .build();

    let client = serenity::ClientBuilder::new(token, intents)
        .framework(framework)
        .await;
    client.unwrap().start().await.unwrap();
}
