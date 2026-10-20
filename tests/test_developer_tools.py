import os
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path
from unittest.mock import Mock, patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame as pg

import config as c
from darkvoid2 import run_app, show_controls
from entities.events import Event
from entities.powerup import PowerUp
from entities.shield import Shield
from game import Game
from systems.highscores import HighScoreTable
from ui.rainbow_text import RainbowText


def key(keycode, **attributes):
    return pg.event.Event(pg.KEYDOWN, key=keycode, **attributes)


class DeveloperToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.game = Game()
        cls.game.highscores = HighScoreTable(Path(cls.temporary.name) / "scores.json")
        c.DEBUG = False

    @classmethod
    def tearDownClass(cls):
        pg.quit()
        cls.temporary.cleanup()

    def setUp(self):
        self.g = self.game
        self.g.console.open = False
        self.g.console.progress = 0
        self.g.console.input = ""
        self.g.console.history.clear()
        self.g.console.history_index = 0
        self.g.console.output.clear()
        self.g.console.cursor_timer = 0.0
        c.event = Event.PLAYING
        self.g.warp_to_stage(1)
        self.g.running = True
        self.g.score = 0
        self.g.highscores.entries = []
        self.g.player.godmode = False
        self.g.player.lives = 3
        self.g.player.invincible_timer = 0
        self.g.player.shield = False
        self.g.player.shield_amount = 0
        self.g.player.vulcan_unlimited = False
        self.g.player.vulcan_heat = 0.0
        self.g.player.vulcan_overheated = False
        self.g.player.vulcan_timer = 0
        self.g.player.vulcan_counter = 0
        self.g.player.reset_powerups()
        self.g.player.power_timer = 0
        self.g.player.railgun_timer = 0

    def test_section_key_and_physical_key_open_console(self):
        for event in (key(0, unicode="\u00a7"), key(pg.K_BACKQUOTE), key(0, scancode=53)):
            self.g.handle_event(event)
            self.assertTrue(self.g.console.open)
            self.g.handle_event(event)
            self.g.console.update(0.3)
            self.assertFalse(self.g.console.active)

    def test_console_freezes_game_until_close_animation_finishes(self):
        self.g.handle_event(key(pg.K_BACKQUOTE))
        self.g.update(0.1)
        self.assertEqual(self.g.level_timer, 0)
        self.g.console.update(0.3)
        self.g.handle_event(key(pg.K_ESCAPE))
        self.g.update(0.1)
        self.assertEqual(self.g.level_timer, 0)
        self.assertTrue(self.g.running)
        self.g.console.update(0.3)
        self.g.update(0.1)
        self.assertGreater(self.g.level_timer, 0)

    def test_console_accepts_text_and_history_without_opening_character(self):
        self.g.handle_event(key(pg.K_BACKQUOTE))
        self.g.handle_event(pg.event.Event(pg.TEXTINPUT, text="\u00a7"))
        self.assertEqual(self.g.console.input, "")
        self.g.handle_event(pg.event.Event(pg.TEXTINPUT, text="god"))
        self.g.handle_event(key(pg.K_RETURN))
        self.assertTrue(self.g.player.godmode)
        self.g.handle_event(pg.event.Event(pg.TEXTINPUT, text="warp 5"))
        self.g.handle_event(key(pg.K_UP))
        self.assertEqual(self.g.console.input, "god")
        self.g.handle_event(key(pg.K_DOWN))
        self.assertEqual(self.g.console.input, "warp 5")

    def test_bad_console_command_keeps_game_alive(self):
        self.g.console.input = "warp 99"
        self.g.console.execute()
        self.assertTrue(self.g.console.output[-1].startswith("Error:"))
        self.assertEqual(self.g.level.stage, 1)
        self.assertTrue(self.g.running)

    def test_god_blocks_direct_bullet_and_body_damage(self):
        self.g.execute_console_command("god")
        self.g.player.hit(killer="test")
        self.g.player.receive_hit(killer="test")
        self.g.damage_player(killer="test")
        bullet = pg.sprite.Sprite(self.g.enemy_bullets, self.g.all_sprites)
        bullet.image = pg.Surface((8, 8))
        bullet.rect = bullet.image.get_rect(center=self.g.player.pos)
        bullet.pos = self.g.player.pos.copy()
        bullet.radius = 4
        bullet.owner = "test"
        self.g.handle_collisions()
        self.assertEqual(self.g.player.lives, 3)
        self.assertTrue(self.g.player.alive)
        self.g.execute_console_command("god")
        self.g.player.receive_hit(killer="test")
        self.assertEqual(self.g.player.lives, 2)

    def test_impulse_grants_weapon_upgrade_and_unlimited_vulcan(self):
        self.g.player.vulcan_heat = self.g.player.vulcan_heat_max
        self.g.player.vulcan_overheated = True
        self.g.player.vulcan_timer = 1
        with patch("game.random.choice", return_value="piercing") as choose:
            result = self.g.execute_console_command("impulse 9")
        self.assertEqual(choose.call_args.args[0], ["spread", "laser", "cannon", "piercing"])
        self.assertTrue(self.g.player.bullets_piercing)
        self.assertIn("piercing", result)
        self.assertTrue(self.g.player.vulcan_unlimited)
        self.assertEqual(self.g.player.vulcan_heat, 0)
        self.assertFalse(self.g.player.vulcan_overheated)
        self.assertEqual(self.g.player.vulcan_timer, 0)

    def test_unlimited_vulcan_keeps_firing_without_heat_buildup(self):
        self.g.execute_console_command("impulse 9")
        with patch("entities.player.pg.mouse.get_pressed", return_value=(0, 0, 1)), \
             patch.object(self.g.player, "spawn_vulcan_fx"), \
             patch.object(self.g.player, "play_vulcan_sound"):
            for _ in range(360):
                self.g.player.update(1 / 60)
                self.g.effects.update(1 / 60)
                self.g.player_bullets.update(1 / 60)
                self.assertFalse(self.g.player.vulcan_overheated)
                self.assertEqual(self.g.player.vulcan_heat, 0)
        self.assertGreater(self.g.player.vulcan_counter, 100)

    def test_powerup_command_grants_two_shield_pickups_and_reports_total(self):
        charges = self.g.level.player_shield_amount
        first = self.g.execute_console_command("powerup shield")
        second = self.g.execute_console_command("powerup shield")
        self.assertEqual(self.g.player.shield_amount, charges * 2)
        self.assertTrue(self.g.player.shield)
        self.assertFalse(self.g.player.shield_active)
        self.assertEqual(first, f"Shield charges: +{charges} (total {charges})")
        self.assertEqual(second, f"Shield charges: +{charges} (total {charges * 2})")

    def test_two_real_shield_pickups_are_collected_and_visible_in_hud(self):
        for _ in range(2):
            powerup = PowerUp(self.g, self.g.player.rect.center, kind="shield")
            self.g.powerups.add(powerup)
            self.g.all_sprites.add(powerup)
            self.g.update(1 / 60)
            self.assertFalse(powerup.groups())
        self.assertEqual(self.g.player.shield_amount, self.g.level.player_shield_amount * 2)
        self.assertIn(f"Shield charges: {self.g.player.shield_amount}", self.g.console.output)
        self.g.screen.fill((0, 0, 0))
        self.g.hud.draw(self.g.screen)
        region = self.g.screen.subsurface((16, 160, 200, 55))
        self.assertNotEqual(pg.image.tobytes(region, "RGB"), bytes(200 * 55 * 3))

    def test_shield_activates_blocks_damage_and_keeps_remaining_charges(self):
        self.g.execute_console_command("powerup shield")
        charges = self.g.player.shield_amount
        self.g.handle_event(key(pg.K_LALT))
        self.assertTrue(self.g.player.shield_active)
        self.assertEqual(self.g.player.shield_amount, charges - 1)
        shields = [effect for effect in self.g.effects if isinstance(effect, Shield)]
        self.assertEqual(len(shields), 1)
        self.g.handle_event(key(pg.K_LALT))
        self.assertEqual(self.g.player.shield_amount, charges - 1)
        self.g.player.receive_hit(killer="test")
        self.assertEqual(self.g.player.lives, 3)
        shields[0].update(5.1)
        self.assertFalse(self.g.player.shield_active)
        self.assertEqual(self.g.player.shield_amount, charges - 1)
        self.g.handle_event(key(pg.K_LALT))
        self.assertTrue(self.g.player.shield_active)
        self.assertEqual(self.g.player.shield_amount, charges - 2)

    def test_powerup_command_accepts_all_supported_types(self):
        for kind in ("shield", "speed", "health", "spread", "laser", "cannon", "piercing"):
            self.assertTrue(self.g.execute_console_command("powerup " + kind))
        self.assertIn("powerup <type>", self.g.execute_console_command("help"))

    def test_bad_powerup_command_does_not_change_inventory(self):
        for command in ("powerup", "powerup unknown", "powerup shield extra"):
            with self.assertRaises(ValueError):
                self.g.execute_console_command(command)
        self.assertEqual(self.g.player.shield_amount, 0)
        self.assertEqual(self.g.player.lives, 3)
        self.assertFalse(self.g.player.speed_boost_active)

    def test_speed_powerup_moves_faster_survives_focus_and_expires(self):
        self.g.player.pos = pg.Vector2(c.WIDTH // 2, c.HEIGHT // 2)
        keys = defaultdict(bool, {pg.K_RIGHT: True})
        self.g.execute_console_command("powerup speed")
        with patch("entities.player.pg.key.get_pressed", return_value=keys), \
             patch("entities.player.pg.mouse.get_pressed", return_value=(0, 0, 0)):
            for focus, speed in ((False, self.g.player.super_speed),
                                 (True, c.PLAYER_FOCUS_SPEED),
                                 (False, self.g.player.super_speed)):
                keys[pg.K_LSHIFT] = focus
                before = self.g.player.pos.x
                self.g.player.update(0.1)
                self.assertAlmostEqual(self.g.player.pos.x - before, speed * 0.1)
            self.g.player.update_powerups(12)
            before = self.g.player.pos.x
            self.g.player.update(0.1)
            self.assertAlmostEqual(self.g.player.pos.x - before, self.g.player.default_speed * 0.1)
        self.assertFalse(self.g.player.speed_boost_active)

    def test_collected_speed_powerup_enables_boost(self):
        powerup = PowerUp(self.g, self.g.player.rect.center, kind="speed")
        self.g.powerups.add(powerup)
        self.g.all_sprites.add(powerup)
        self.g.update(1 / 60)
        self.g.player.update(1 / 60)
        self.assertTrue(self.g.player.speed_boost_active)
        self.assertEqual(self.g.player.speed, self.g.player.super_speed)

    def test_normal_vulcan_still_overheats_and_recovers(self):
        self.g.player.update_vulcan_heat(6, firing=True)
        self.assertTrue(self.g.player.vulcan_overheated)
        self.assertEqual(self.g.player.vulcan_heat, self.g.player.vulcan_heat_max)
        self.g.player.update_vulcan_heat(10, firing=False)
        self.assertFalse(self.g.player.vulcan_overheated)
        self.assertEqual(self.g.player.vulcan_heat, 0)

    def test_unlimited_vulcan_survives_powerup_expiration_and_warp(self):
        self.g.execute_console_command("impulse 9")
        self.g.player.update_powerups(13)
        self.assertTrue(self.g.player.vulcan_unlimited)
        self.g.warp_to_stage(5)
        self.assertTrue(self.g.player.vulcan_unlimited)

    def test_warp_rebuilds_boss_queue_for_each_stage(self):
        for stage in range(1, 6):
            self.g.execute_console_command(f"warp {stage}")
            self.assertEqual(self.g.level.stage, stage)
            self.assertEqual(c.BOSS[0]["lvl"], stage)
            self.assertEqual(self.g.world_phase, "terrain" if stage == 5 else "space")
            self.g.update(1 / 60)
            self.g.draw()

    def test_warp_clears_old_sprites_and_restores_dead_player(self):
        self.g.end_game()
        self.g.player.lives = 0
        old = pg.sprite.Sprite(self.g.enemy_bullets, self.g.all_sprites)
        self.g.execute_console_command("warp 5")
        self.assertFalse(old.groups())
        self.assertTrue(self.g.player.alive)
        self.assertTrue(self.g.player.visible)
        self.assertEqual(self.g.player.lives, c.PLAYER_LIVES)
        self.assertFalse(self.g.ending_active)
        self.assertIn(self.g.player, self.g.all_sprites)

    def test_invalid_warp_does_not_mutate_game(self):
        for command in ("warp", "warp -1", "warp 6", "warp nope", "impulse 8", "god on"):
            with self.assertRaises(ValueError):
                self.g.execute_console_command(command)
            self.assertEqual(self.g.level.stage, 1)
            self.assertEqual(c.BOSS[0]["lvl"], 1)

    def spawn_stage_boss(self):
        boss = c.BOSS.pop(0)
        return self.g.boss_spawn(name=boss["name"], lvl=boss["lvl"],
                                 image=boss["boss_image"], hp=boss["boss_hp"], pos=boss["pos"])

    def test_stage_four_still_transitions_to_terrain(self):
        self.g.warp_to_stage(4)
        self.spawn_stage_boss().destroy()
        self.assertEqual(self.g.world_phase, "boss_explosion")
        self.assertFalse(self.g.ending_active)
        self.assertTrue(self.g.player.alive)
        for _ in range(1800):
            self.g.update(1 / 60)
            if self.g.world_phase == "terrain":
                break
        self.assertEqual(self.g.world_phase, "terrain")
        self.assertEqual(self.g.level.stage, 5)

    def test_last_boss_reaches_name_entry_and_saves_stage_five(self):
        self.g.warp_to_stage(5)
        boss = self.spawn_stage_boss()
        boss.destroy()
        boss.destroy()
        self.assertEqual(self.g.score, 5000)
        self.assertTrue(self.g.victory)
        self.assertFalse(self.g.highscore_sequence_started)
        self.assertEqual(self.g.level.stage, 5)
        self.g.player.update(1 / 60)
        for _ in range(310):
            self.g.update(1 / 60)
        self.g.draw()
        self.assertTrue(self.g.entering_highscore)
        self.g.handle_event(pg.event.Event(pg.TEXTINPUT, text="TEST"))
        self.g.handle_event(key(pg.K_RETURN))
        entries = HighScoreTable(self.g.highscores.path).entries
        self.assertEqual(entries[0], {"name": "TEST", "score": 5000, "level": 5, "killed_by": "No-one"})

    def test_terrain_death_also_reaches_name_entry(self):
        self.g.warp_to_stage(5)
        self.g.player.invincible_timer = 0
        self.g.player.lives = 1
        self.g.player.receive_hit(killer="Terrain Automaton")
        self.g.update(5.1)
        self.g.draw()
        self.assertTrue(self.g.entering_highscore)
        self.assertEqual(self.g.killed_by, "Terrain Automaton")
        self.assertFalse(self.g.victory)

    def test_escape_does_not_create_unrequested_score(self):
        self.g.handle_event(key(pg.K_ESCAPE))
        self.assertFalse(self.g.running)
        self.assertFalse(self.g.highscores.entries)

    def test_highscore_space_requests_restart(self):
        self.g.show_highscores = True
        with patch("game.pg.event.get", return_value=[key(pg.K_SPACE)]):
            self.assertEqual(self.g.run(), "restart")
        self.assertTrue(self.g.restart_requested)

    def test_name_entry_space_does_not_restart_before_name_is_saved(self):
        self.g.show_highscores = True
        self.g.entering_highscore = True
        self.g.handle_event(key(pg.K_SPACE))
        self.g.handle_event(pg.event.Event(pg.TEXTINPUT, text=" "))
        self.assertTrue(self.g.running)
        self.assertFalse(self.g.restart_requested)
        self.assertEqual(self.g.highscore_name, " ")

    def test_new_game_resets_progress_and_keeps_ship_intro(self):
        self.g.warp_to_stage(5)
        self.g.score = 99999
        self.g.player.godmode = True
        self.g.player.vulcan_unlimited = True
        self.g.player.apply_powerup("spread")
        fresh = Game()
        self.assertEqual(fresh.level.stage, 1)
        self.assertEqual(fresh.score, 0)
        self.assertEqual(fresh.world_phase, "space")
        self.assertEqual(c.BOSS[0]["lvl"], 1)
        self.assertEqual(fresh.player.lives, c.PLAYER_LIVES)
        self.assertEqual(fresh.player.shoot_mode, "normal")
        self.assertFalse(fresh.player.godmode)
        self.assertFalse(fresh.player.vulcan_unlimited)
        self.assertFalse(fresh.console.active)
        self.assertTrue(fresh.player.intro_active)
        self.assertGreater(fresh.player.current_scale, fresh.player.final_scale)
        initial_width = fresh.player.image.get_width()
        fresh.player.update_intro(c.PLAYER_INTRO_RISE_TIME)
        fresh.player.update_intro(c.PLAYER_INTRO_SCALE_TIME / 2)
        self.assertLess(fresh.player.image.get_width(), initial_width)
        self.assertGreater(fresh.player.current_scale, fresh.player.final_scale)
        fresh.player.update_intro(c.PLAYER_INTRO_SCALE_TIME / 2)
        self.assertFalse(fresh.player.intro_active)
        self.assertTrue(fresh.player.intro_done)
        self.assertEqual(fresh.player.current_scale, c.PLAYER_SCALE)

    def test_name_entry_clips_pasted_text_and_does_not_activate_shield(self):
        self.g.entering_highscore = True
        self.g.player.shield_amount = 1
        self.g.handle_event(key(pg.K_LALT))
        self.assertFalse(self.g.player.shield_active)
        self.g.handle_event(pg.event.Event(pg.TEXTINPUT, text="abcdefghijklmnop"))
        self.assertEqual(self.g.highscore_name, "abcdefghijkl")

    def test_console_blocks_shield_input_until_closed(self):
        self.g.player.apply_powerup("shield")
        self.g.handle_event(key(pg.K_BACKQUOTE))
        self.g.console.update(0.3)
        self.g.handle_event(key(pg.K_LALT))
        self.assertFalse(self.g.player.shield_active)
        self.g.handle_event(key(pg.K_ESCAPE))
        self.g.console.update(0.3)
        self.g.handle_event(key(pg.K_LALT))
        self.assertTrue(self.g.player.shield_active)
        self.g.draw()

    def test_highscore_screen_replaces_ending_banner(self):
        self.g.end_game(victory=True)
        self.g.update(5.1)
        with patch.object(self.g, "draw_ending_banner") as ending, \
             patch.object(self.g.hud, "draw_highscores") as scores:
            self.g.draw()
        ending.assert_not_called()
        scores.assert_called_once()

    def test_real_loop_pauses_audio_and_resumes_after_console_closes(self):
        events = [[key(pg.K_BACKQUOTE)], [], [key(pg.K_ESCAPE)], [], [], [pg.event.Event(pg.QUIT)]]
        with patch.object(self.g, "clock", Mock(tick=Mock(return_value=100))), \
             patch("game.pg.event.get", side_effect=events), \
             patch.object(self.g, "draw"), patch.object(self.g, "update") as update, \
             patch("game.mixer.pause") as pause, patch("game.mixer.unpause") as unpause:
            self.assertEqual(self.g.run(), "quit")
        self.assertEqual(update.call_count, 2)
        pause.assert_called_once()
        unpause.assert_called_once()

    def test_manual_pause_is_preserved_by_console(self):
        c.event = Event.PAUSE
        self.g.handle_event(key(pg.K_BACKQUOTE))
        self.g.console.update(0.3)
        self.g.handle_event(key(pg.K_ESCAPE))
        self.g.console.update(0.3)
        self.assertEqual(c.event, Event.PAUSE)

    def test_console_backdrop_is_half_opacity(self):
        screen = pg.Surface((800, 600))
        screen.fill((200, 100, 50))
        self.g.console.toggle()
        self.g.console.update(0.3)
        self.g.console.draw(screen)
        self.assertEqual(screen.get_at((799, 301))[:3], (100, 50, 25))
        self.assertEqual(screen.get_at((799, 299))[:3], (200, 100, 50))

    def test_console_prompt_and_history_are_green_with_white_input(self):
        screen = pg.Surface((800, 600))
        self.g.console.toggle()
        self.g.console.update(0.3)
        self.g.console.input = "god"
        self.g.console.write("> warp 5")
        self.g.console.draw(screen)
        font = self.g.console.font
        line_height = font.get_linesize()
        y = 600 - line_height - 16
        prompt_width = font.size("> ")[0]
        for line_y in (y, y - line_height):
            region = screen.subsurface((24, line_y, prompt_width, line_height))
            self.assertGreater(pg.mask.from_threshold(region, (0, 255, 0), (1, 1, 1, 255)).count(), 0)
        text = screen.subsurface((24 + prompt_width, y, font.size("god")[0], line_height))
        self.assertGreater(pg.mask.from_threshold(text, (255, 255, 255), (1, 1, 1, 255)).count(), 0)

    def test_console_cursor_blinks_while_game_is_paused(self):
        self.g.console.toggle()
        self.g.console.update(0.3)
        self.g.console.input = "god"
        font = self.g.console.font
        cursor_rect = pg.Rect(24 + font.size("> god")[0],
                              600 - font.get_linesize() - 16,
                              font.size("_")[0], font.get_linesize())
        frames = []
        for delta in (0, 0.2, 0.5):
            self.g.console.update(delta)
            self.g.update(delta)
            screen = pg.Surface((800, 600))
            self.g.console.draw(screen)
            frames.append(screen)
        self.assertGreater(pg.mask.from_threshold(frames[0].subsurface(cursor_rect),
                                                 (255, 255, 255), (1, 1, 1, 255)).count(), 0)
        self.assertEqual(pg.mask.from_threshold(frames[1].subsurface(cursor_rect),
                                               (255, 255, 255), (1, 1, 1, 255)).count(), 0)
        self.assertEqual(pg.image.tobytes(frames[0], "RGB"), pg.image.tobytes(frames[2], "RGB"))
        self.assertEqual(self.g.level_timer, 0)

    def test_console_long_input_does_not_shift_when_cursor_blinks(self):
        self.g.console.toggle()
        self.g.console.update(0.3)
        self.g.console.input = "W" * 128
        inputs = []
        for delta in (0, 0.2):
            self.g.console.update(delta)
            with patch.object(self.g.console, "font", wraps=self.g.console.font) as font:
                self.g.console.draw(pg.Surface((320, 600)))
                inputs.append(next(call.args[0] for call in font.render.call_args_list
                                   if call.args[2] == (255, 255, 255) and call.args[0] != "_"))
        self.assertEqual(inputs[0], inputs[1])
        self.assertLess(len(inputs[0]), 128)
        self.assertLessEqual(self.g.console.font.size("> " + inputs[0] + "_")[0], 320 - 48)

    def test_console_cursor_reappears_when_typing_and_reopening(self):
        self.g.console.toggle()
        self.g.console.update(0.6)
        self.assertGreaterEqual(self.g.console.cursor_timer, 0.5)
        self.g.console.handle_event(pg.event.Event(pg.TEXTINPUT, text="god"))
        self.assertEqual(self.g.console.cursor_timer, 0)
        self.g.console.update(0.6)
        self.g.console.handle_event(key(pg.K_BACKSPACE))
        self.assertEqual(self.g.console.cursor_timer, 0)
        self.g.console.update(0.6)
        self.g.console.toggle()
        self.g.console.toggle()
        self.assertEqual(self.g.console.cursor_timer, 0)

    def test_controls_exit_events(self):
        for event, result in ((key(pg.K_SPACE), True), (key(pg.K_ESCAPE), False), (pg.event.Event(pg.QUIT), False)):
            with patch("darkvoid2.pg.event.get", return_value=[event]):
                self.assertEqual(show_controls(self.g.screen, self.g.medium_nerd, self.g.small_nerd), result)


class AppFlowTests(unittest.TestCase):
    def test_restarts_create_fresh_games_without_replaying_opening_demo(self):
        games = [Mock(run=Mock(return_value=result)) for result in ("restart", "restart", "quit")]
        with patch("darkvoid2.alpha", return_value=True) as intro, \
             patch("darkvoid2.Game", side_effect=games) as factory, \
             patch("darkvoid2.pg.quit") as quit_display, \
             patch("darkvoid2.pg.mixer.quit") as quit_audio:
            run_app()
        intro.assert_called_once()
        self.assertEqual(factory.call_count, 3)
        for game in games:
            game.run.assert_called_once()
        quit_display.assert_called_once()
        quit_audio.assert_called_once()

    def test_cancelled_opening_demo_does_not_start_game(self):
        with patch("darkvoid2.alpha", return_value=False) as intro, \
             patch("darkvoid2.Game") as factory, \
             patch("darkvoid2.pg.quit"), patch("darkvoid2.pg.mixer.quit"):
            run_app()
        intro.assert_called_once()
        factory.assert_not_called()


class RainbowTextTests(unittest.TestCase):
    def test_full_spectrum_stays_colored_with_motion_and_alpha(self):
        mask = pg.Surface((700, 100), pg.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        rainbow = RainbowText(mask)
        initial = rainbow.render(0).copy()
        self.assertEqual(initial.get_at((50, 50)), initial.get_at((75, 25)))
        self.assertNotEqual(initial.get_at((20, 20)), initial.get_at((300, 20)))
        self.assertNotEqual(initial.get_at((20, 20)), rainbow.render(1).get_at((20, 20)))
        for time in (0, 0.5, 2, 4, 6, 8):
            frame = rainbow.render(time)
            for x in range(0, 700, 23):
                color = frame.get_at((x, 50))[:3]
                self.assertGreaterEqual(min(color), 85)
                self.assertGreaterEqual(max(color) - min(color), 160)
        mask.set_at((0, 0), (255, 255, 255, 0))
        self.assertEqual(rainbow.render(0).get_at((0, 0)).a, 0)
        mask.set_at((0, 0), (255, 255, 255, 255))
        self.assertEqual(rainbow.render(0).get_at((0, 0)).a, 255)

    def test_gradient_moves_from_upper_left_to_lower_right(self):
        mask = pg.Surface((100, 100), pg.SRCALPHA)
        mask.fill((255, 255, 255, 255))
        rainbow = RainbowText(mask, speed=70)
        initial = rainbow.render(0).copy()
        moved = rainbow.render(1)
        self.assertEqual(initial.get_at((20, 20)), moved.get_at((55, 55)))
        self.assertNotEqual(initial.get_at((20, 20)), moved.get_at((20, 20)))


if __name__ == "__main__":
    unittest.main()
