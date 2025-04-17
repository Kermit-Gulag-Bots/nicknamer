use poise::serenity_prelude::UserId;

mod config;

///    This function handles the 'nick' command for the `nicknamer` bot. Its purpose is to \
///     allow discord users to manage each other's nicknames, even if they are in the same \
///     Discord Role. The bot applies any nickname changes as specified by this command. \
///     This command assumes that the bot has a higher Role than all users which invoke this \
///     command. \
///     In certain failure scenarios, such as offering an invalid nickname, the bot will \
///     reply with information about the invalid command.
#[allow(dead_code)]
pub fn nick(_user_id: UserId) {
    todo!()
}
