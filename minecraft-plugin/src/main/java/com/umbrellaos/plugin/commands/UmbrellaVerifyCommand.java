package com.umbrellaos.plugin.commands;

import com.umbrellaos.plugin.UmbrellaPlugin;
import com.umbrellaos.plugin.api.CoreApiClient;
import org.bukkit.Bukkit;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;

/** /umbrellaverify and /umbrellaunlink — manual Discord<->MC linking.
 *  Gated behind umbrellaos.verify, separate from umbrellaos.staff. */
public class UmbrellaVerifyCommand implements CommandExecutor {
    private final CoreApiClient apiClient;
    private final UmbrellaPlugin plugin;

    public UmbrellaVerifyCommand(CoreApiClient apiClient, UmbrellaPlugin plugin) {
        this.apiClient = apiClient;
        this.plugin = plugin;
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!sender.hasPermission("umbrellaos.verify")) {
            sender.sendMessage("\u00a7cYou don't have permission to use this command.");
            return true;
        }

        if (label.equalsIgnoreCase("umbrellaverify")) {
            if (args.length != 2) {
                sender.sendMessage("\u00a7eUsage: /umbrellaverify <discordId> <mcUsername>");
                return true;
            }
            String discordId = args[0];
            String mcUsername = args[1];
            sender.sendMessage("\u00a77Linking " + discordId + " -> " + mcUsername + "...");
            apiClient.manualLink(discordId, mcUsername).thenAccept(result ->
                Bukkit.getScheduler().runTask(plugin, () ->
                    sender.sendMessage("\u00a7aLinked " + discordId + " to " + mcUsername
                            + ". UUID resolves on their next join."))
            ).exceptionally(e -> {
                Bukkit.getScheduler().runTask(plugin, () ->
                    sender.sendMessage("\u00a7cFailed: " + e.getMessage()));
                return null;
            });
            return true;
        }

        if (label.equalsIgnoreCase("umbrellaunlink")) {
            if (args.length != 1) {
                sender.sendMessage("\u00a7eUsage: /umbrellaunlink <discordId>");
                return true;
            }
            String discordId = args[0];
            apiClient.unlinkAccount(discordId).thenAccept(result ->
                Bukkit.getScheduler().runTask(plugin, () ->
                    sender.sendMessage("\u00a7aUnlinked " + discordId + "."))
            ).exceptionally(e -> {
                Bukkit.getScheduler().runTask(plugin, () ->
                    sender.sendMessage("\u00a7cFailed: " + e.getMessage()));
                return null;
            });
            return true;
        }

        return false;
    }
}
