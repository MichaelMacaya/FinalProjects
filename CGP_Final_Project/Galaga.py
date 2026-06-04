import tkinter as tk
import random
import math

class GalagaGame:
    def __init__(self, root):
        self.root = root
        self.root.title("GALAGA - Classic Arcade")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Game constants
        self.WIDTH = 600
        self.HEIGHT = 700
        self.PLAYER_SPEED = 5
        self.BULLET_SPEED = 12
        self.BOSS_LEVEL = 5
        
        # Colors - Classic arcade palette
        self.BG_COLOR = "#000000"
        self.PLAYER_COLOR = "#FFFFFF"
        self.PLAYER_ACCENT = "#FF0000"
        self.BULLET_COLOR = "#FFFF00"
        self.ENEMY_BULLET_COLOR = "#FF4444"
        self.STAR_COLOR = "#FFFFFF"
        
        # Enemy colors from image
        self.ENEMY_BLUE_BODY = "#4444FF"
        self.ENEMY_BLUE_ACCENT = "#FF44FF"
        self.ENEMY_RED_BODY = "#FF0000"
        self.ENEMY_RED_ACCENT = "#FFFFFF"
        self.ENEMY_GREEN_BODY = "#00FF00"
        self.ENEMY_GREEN_ACCENT = "#FF00FF"
        self.ENEMY_YELLOW_BODY = "#FFFF00"
        self.ENEMY_YELLOW_ACCENT = "#FF8800"
        self.ENEMY_CYAN_BODY = "#00FFFF"
        self.ENEMY_CYAN_ACCENT = "#FF8800"
        self.ENEMY_ORANGE_BODY = "#FF8800"
        self.ENEMY_ORANGE_ACCENT = "#FFFF00"
        
        # Boss colors
        self.BOSS_COLOR = "#CC0000"
        self.BOSS_ACCENT = "#FF4400"
        
        # Canvas setup
        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg=self.BG_COLOR)
        self.canvas.pack()
        
        # Game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = 0
        self.game_running = False
        self.paused = False
        self.invulnerable = False
        self.boss_mode = False
        self.boss = None
        self.boss_health = 0
        self.boss_max_health = 0
        
        # Player
        self.player = None
        self.player_x = self.WIDTH // 2
        self.player_y = self.HEIGHT - 80
        self.player_vel_x = 0
        
        # Lists for game objects
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.stars = []
        self.particles = []
        
        # UI elements tracking
        self.title_text = None
        self.subtitle_text = None
        self.game_over_text = None
        self.game_over_subtext = None
        self.pause_text = None
        self.level_text_display = None
        self.boss_health_bar = None
        self.boss_health_bg = None
        self.you_win_text = None
        self.you_win_subtext = None
        
        # Input handling
        self.keys_pressed = set()
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.bind("<space>", self.shoot)
        self.root.bind("<p>", self.toggle_pause)
        self.root.bind("<Return>", self.start_game)
        
        # Create UI
        self.create_ui()
        self.create_stars()
        self.show_title_screen()
        
        # Game loop
        self.game_loop_id = None
    
    def create_ui(self):
        # 1UP Score
        self.score_label = self.canvas.create_text(
            50, 15, anchor="n", text="1UP", 
            fill="#FF0000", font=("Courier", 12, "bold")
        )
        self.score_text = self.canvas.create_text(
            50, 30, anchor="n", text="00000", 
            fill="#FFFFFF", font=("Courier", 14, "bold")
        )
        # High Score
        self.high_label = self.canvas.create_text(
            self.WIDTH // 2, 15, anchor="n", text="HIGH SCORE", 
            fill="#FF0000", font=("Courier", 12, "bold")
        )
        self.high_text = self.canvas.create_text(
            self.WIDTH // 2, 30, anchor="n", text="00000", 
            fill="#FFFFFF", font=("Courier", 14, "bold")
        )
        # Lives
        self.lives_text = self.canvas.create_text(
            self.WIDTH - 50, 30, anchor="n", text="3", 
            fill="#FFFFFF", font=("Courier", 14, "bold")
        )
    
    def create_stars(self):
        for _ in range(150):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            size = random.choice([1, 1, 1, 2])
            brightness = random.choice(["#444444", "#666666", "#888888", "#AAAAAA", "#FFFFFF"])
            star = self.canvas.create_oval(
                x, y, x+size, y+size, fill=brightness, outline=""
            )
            self.stars.append({"id": star, "x": x, "y": y, "speed": random.uniform(0.3, 2.5)})
    
    def clear_all_texts(self):
        texts = [
            self.title_text, self.subtitle_text, self.game_over_text,
            self.game_over_subtext, self.pause_text, self.level_text_display,
            self.you_win_text, self.you_win_subtext
        ]
        for text in texts:
            if text:
                self.canvas.delete(text)
        
        self.title_text = None
        self.subtitle_text = None
        self.game_over_text = None
        self.game_over_subtext = None
        self.pause_text = None
        self.level_text_display = None
        self.you_win_text = None
        self.you_win_subtext = None
    
    def clear_boss_ui(self):
        if self.boss_health_bar:
            self.canvas.delete(self.boss_health_bar)
            self.boss_health_bar = None
        if self.boss_health_bg:
            self.canvas.delete(self.boss_health_bg)
            self.boss_health_bg = None
    
    def show_title_screen(self):
        self.clear_all_texts()
        self.clear_boss_ui()
        self.title_text = self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 3 - 40,
            text="GALAGA", fill="#00FF00",
            font=("Courier", 56, "bold")
        )
        self.subtitle_text = self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 2 - 20,
            text="PUSH START BUTTON\n\n1 COIN 1 PLAY\n\nCONTROLS:\n← → MOVE\nSPACE FIRE\nP PAUSE",
            fill="#FFFFFF", font=("Courier", 16)
        )
    
    def start_game(self, event=None):
        if self.game_running:
            return
        
        self.clear_all_texts()
        self.clear_boss_ui()
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_running = True
        self.paused = False
        self.invulnerable = False
        self.boss_mode = False
        self.boss = None
        self.player_vel_x = 0
        
        self.update_ui()
        
        self.create_player()
        
        self.clear_enemies()
        self.clear_bullets()
        self.clear_particles()
        
        if self.level % self.BOSS_LEVEL == 0:
            self.spawn_boss()
        else:
            self.spawn_enemies()
        
        self.game_loop()
    
    def clear_enemies(self):
        for enemy in self.enemies:
            for part in enemy.get("parts", []):
                self.canvas.delete(part)
        self.enemies.clear()
    
    def clear_bullets(self):
        for bullet in self.bullets:
            self.canvas.delete(bullet["id"])
        self.bullets.clear()
        for bullet in self.enemy_bullets:
            self.canvas.delete(bullet["id"])
        self.enemy_bullets.clear()
    
    def clear_particles(self):
        for p in self.particles:
            self.canvas.delete(p["id"])
        self.particles.clear()
    
    def create_player(self):
        parts = ['player_body', 'player_wing_l', 'player_wing_r', 'player_cockpit', 'player_engine']
        for part in parts:
            if hasattr(self, part):
                p = getattr(self, part)
                if p:
                    self.canvas.delete(p)
                    setattr(self, part, None)
        
        x, y = self.player_x, self.player_y
        
        # Classic Galaga player ship
        self.player_body = self.canvas.create_polygon(
            x, y - 20,
            x - 5, y - 10,
            x - 8, y + 5,
            x - 12, y + 15,
            x - 20, y + 20,
            x - 8, y + 20,
            x - 3, y + 10,
            x, y + 15,
            x + 3, y + 10,
            x + 8, y + 20,
            x + 20, y + 20,
            x + 12, y + 15,
            x + 8, y + 5,
            x + 5, y - 10,
            fill=self.PLAYER_COLOR, outline="#CCCCCC", width=1
        )
        
        self.player_wing_l = self.canvas.create_polygon(
            x - 12, y + 15,
            x - 20, y + 20,
            x - 8, y + 20,
            fill=self.PLAYER_ACCENT, outline=""
        )
        self.player_wing_r = self.canvas.create_polygon(
            x + 12, y + 15,
            x + 20, y + 20,
            x + 8, y + 20,
            fill=self.PLAYER_ACCENT, outline=""
        )
        
        self.player_cockpit = self.canvas.create_oval(
            x - 3, y - 8, x + 3, y + 2,
            fill="#4444FF", outline="#6666FF", width=1
        )
        
        self.player_engine = self.canvas.create_oval(
            x - 4, y + 15, x + 4, y + 25,
            fill="#FF6600", outline="#FFAA00", width=1
        )
    
    def create_enemy_purple_crab(self, x, y):
        """Top-left: Purple/Blue crab-like alien"""
        parts = []
        # Body
        body = self.canvas.create_polygon(
            x, y - 15,
            x - 10, y - 10,
            x - 15, y,
            x - 10, y + 10,
            x - 5, y + 15,
            x, y + 10,
            x + 5, y + 15,
            x + 10, y + 10,
            x + 15, y,
            x + 10, y - 10,
            fill=self.ENEMY_BLUE_BODY, outline="#FFFFFF", width=1
        )
        parts.append(body)
        # Purple center
        center = self.canvas.create_polygon(
            x - 5, y - 5,
            x + 5, y - 5,
            x + 5, y + 5,
            x - 5, y + 5,
            fill=self.ENEMY_BLUE_ACCENT, outline=""
        )
        parts.append(center)
        # Eyes
        eye_l = self.canvas.create_oval(x - 8, y - 8, x - 4, y - 4, fill="#FFFFFF", outline="")
        eye_r = self.canvas.create_oval(x + 4, y - 8, x + 8, y - 4, fill="#FFFFFF", outline="")
        parts.extend([eye_l, eye_r])
        # Legs
        for offset in [-12, -6, 0, 6, 12]:
            leg = self.canvas.create_line(
                x + offset, y + 10, x + offset, y + 18,
                fill=self.ENEMY_BLUE_ACCENT, width=2
            )
            parts.append(leg)
        return parts
    
    def create_enemy_red_scorpion(self, x, y):
        """Top-middle: Red scorpion-like alien"""
        parts = []
        # Body
        body = self.canvas.create_polygon(
            x, y - 18,
            x - 12, y - 10,
            x - 18, y,
            x - 12, y + 10,
            x - 6, y + 15,
            x, y + 10,
            x + 6, y + 15,
            x + 12, y + 10,
            x + 18, y,
            x + 12, y - 10,
            fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1
        )
        parts.append(body)
        # White stripes
        stripe1 = self.canvas.create_rectangle(x - 10, y - 5, x + 10, y + 2, fill="#FFFFFF", outline="")
        stripe2 = self.canvas.create_rectangle(x - 8, y + 5, x + 8, y + 10, fill="#4444FF", outline="")
        parts.extend([stripe1, stripe2])
        # Claws
        claw_l = self.canvas.create_polygon(
            x - 15, y - 5, x - 22, y - 12, x - 18, y - 2,
            fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1
        )
        claw_r = self.canvas.create_polygon(
            x + 15, y - 5, x + 22, y - 12, x + 18, y - 2,
            fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1
        )
        parts.extend([claw_l, claw_r])
        # Tail
        tail = self.canvas.create_polygon(
            x, y + 10, x - 3, y + 20, x, y + 25, x + 3, y + 20,
            fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1
        )
        parts.append(tail)
        return parts
    
    def create_enemy_blue_butterfly(self, x, y):
        """Top-right: Blue butterfly alien"""
        parts = []
        # Wings
        wing_l = self.canvas.create_polygon(
            x - 5, y - 5,
            x - 20, y - 15,
            x - 25, y,
            x - 20, y + 10,
            x - 10, y + 5,
            fill=self.ENEMY_BLUE_BODY, outline="#FFFFFF", width=1
        )
        wing_r = self.canvas.create_polygon(
            x + 5, y - 5,
            x + 20, y - 15,
            x + 25, y,
            x + 20, y + 10,
            x + 10, y + 5,
            fill=self.ENEMY_BLUE_BODY, outline="#FFFFFF", width=1
        )
        # Body
        body = self.canvas.create_polygon(
            x, y - 12,
            x - 4, y - 5,
            x - 4, y + 5,
            x, y + 12,
            x + 4, y + 5,
            x + 4, y - 5,
            fill=self.ENEMY_YELLOW_BODY, outline="#FFFFFF", width=1
        )
        # Head
        head = self.canvas.create_oval(x - 5, y - 15, x + 5, y - 8, fill=self.ENEMY_RED_BODY, outline="")
        parts.extend([wing_l, wing_r, body, head])
        return parts
    
    def create_enemy_yellow_bee(self, x, y):
        """Middle-left: Yellow bee-like alien"""
        parts = []
        # Body
        body = self.canvas.create_polygon(
            x, y - 15,
            x - 8, y - 8,
            x - 12, y,
            x - 8, y + 8,
            x, y + 15,
            x + 8, y + 8,
            x + 12, y,
            x + 8, y - 8,
            fill=self.ENEMY_YELLOW_BODY, outline="#FFFFFF", width=1
        )
        parts.append(body)
        # Wings
        wing_l = self.canvas.create_polygon(
            x - 5, y - 5, x - 15, y - 12, x - 12, y, x - 8, y + 2,
            fill=self.ENEMY_BLUE_BODY, outline="#FFFFFF", width=1
        )
        wing_r = self.canvas.create_polygon(
            x + 5, y - 5, x + 15, y - 12, x + 12, y, x + 8, y + 2,
            fill=self.ENEMY_BLUE_BODY, outline="#FFFFFF", width=1
        )
        parts.extend([wing_l, wing_r])
        # Stinger
        stinger = self.canvas.create_polygon(
            x - 2, y + 12, x, y + 22, x + 2, y + 12,
            fill=self.ENEMY_YELLOW_ACCENT, outline="#FFFFFF", width=1
        )
        parts.append(stinger)
        return parts
    
    def create_enemy_red_white_bird(self, x, y):
        """Middle-center: Red/White bird-like alien"""
        parts = []
        # Body (white)
        body = self.canvas.create_polygon(
            x, y - 20,
            x - 10, y - 10,
            x - 15, y,
            x - 10, y + 10,
            x, y + 15,
            x + 10, y + 10,
            x + 15, y,
            x + 10, y - 10,
            fill="#FFFFFF", outline="#FFFFFF", width=1
        )
        parts.append(body)
        # Wings (red)
        wing_l = self.canvas.create_polygon(
            x - 8, y - 5, x - 25, y - 15, x - 20, y, x - 12, y + 5,
            fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1
        )
        wing_r = self.canvas.create_polygon(
            x + 8, y - 5, x + 25, y - 15, x + 20, y, x + 12, y + 5,
            fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1
        )
        parts.extend([wing_l, wing_r])
        # Red center
        center = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=self.ENEMY_RED_BODY, outline="")
        parts.append(center)
        return parts
    
    def create_enemy_cyan_scorpion(self, x, y):
        """Middle-right: Cyan/Yellow scorpion alien"""
        parts = []
        # Body
        body = self.canvas.create_polygon(
            x, y - 12,
            x - 8, y - 6,
            x - 12, y,
            x - 8, y + 6,
            x, y + 12,
            x + 8, y + 6,
            x + 12, y,
            x + 8, y - 6,
            fill=self.ENEMY_CYAN_BODY, outline="#FFFFFF", width=1
        )
        parts.append(body)
        # Claws
        claw_l = self.canvas.create_polygon(
            x - 10, y - 5, x - 18, y - 12, x - 14, y - 2,
            fill=self.ENEMY_CYAN_ACCENT, outline="#FFFFFF", width=1
        )
        claw_r = self.canvas.create_polygon(
            x + 10, y - 5, x + 18, y - 12, x + 14, y - 2,
            fill=self.ENEMY_CYAN_ACCENT, outline="#FFFFFF", width=1
        )
        parts.extend([claw_l, claw_r])
        # Tail
        tail = self.canvas.create_polygon(
            x, y + 10, x - 3, y + 20, x, y + 28, x + 3, y + 20,
            fill=self.ENEMY_CYAN_ACCENT, outline="#FFFFFF", width=1
        )
        parts.append(tail)
        return parts
    
    def create_enemy_green_bug(self, x, y):
        """Bottom-left: Green bug alien"""
        parts = []
        # Body
        body = self.canvas.create_polygon(
            x, y - 15,
            x - 12, y - 8,
            x - 18, y,
            x - 12, y + 8,
            x - 6, y + 15,
            x, y + 10,
            x + 6, y + 15,
            x + 12, y + 8,
            x + 18, y,
            x + 12, y - 8,
            fill=self.ENEMY_GREEN_BODY, outline="#FFFFFF", width=1
        )
        parts.append(body)
        # Pink center
        center = self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=self.ENEMY_GREEN_ACCENT, outline="")
        parts.append(center)
        # Eyes
        eye_l = self.canvas.create_oval(x - 8, y - 10, x - 4, y - 6, fill="#FFFFFF", outline="")
        eye_r = self.canvas.create_oval(x + 4, y - 10, x + 8, y - 6, fill="#FFFFFF", outline="")
        parts.extend([eye_l, eye_r])
        # Legs
        for offset in [-10, -5, 0, 5, 10]:
            leg = self.canvas.create_line(
                x + offset, y + 10, x + offset, y + 20,
                fill=self.ENEMY_GREEN_ACCENT, width=2
            )
            parts.append(leg)
        return parts
    
    def create_enemy_blue_dragonfly(self, x, y):
        """Bottom-middle: Blue dragonfly alien"""
        parts = []
        # Body
        body = self.canvas.create_polygon(
            x, y - 20,
            x - 3, y - 10,
            x - 3, y + 10,
            x, y + 20,
            x + 3, y + 10,
            x + 3, y - 10,
            fill=self.ENEMY_BLUE_BODY, outline="#FFFFFF", width=1
        )
        parts.append(body)
        # Wings (white/blue)
        wing_l = self.canvas.create_polygon(
            x - 3, y - 5, x - 20, y - 10, x - 25, y, x - 20, y + 5, x - 3, y + 2,
            fill="#FFFFFF", outline="#4444FF", width=1
        )
        wing_r = self.canvas.create_polygon(
            x + 3, y - 5, x + 20, y - 10, x + 25, y, x + 20, y + 5, x + 3, y + 2,
            fill="#FFFFFF", outline="#4444FF", width=1
        )
        parts.extend([wing_l, wing_r])
        # Head
        head = self.canvas.create_oval(x - 4, y - 22, x + 4, y - 16, fill=self.ENEMY_RED_BODY, outline="")
        parts.append(head)
        return parts
    
    def create_enemy_blue_boss(self, x, y):
        """Bottom-right: Blue boss alien"""
        parts = []
        # Main body
        body = self.canvas.create_polygon(
            x, y - 20,
            x - 15, y - 10,
            x - 20, y,
            x - 15, y + 10,
            x - 8, y + 15,
            x, y + 20,
            x + 8, y + 15,
            x + 15, y + 10,
            x + 20, y,
            x + 15, y - 10,
            fill=self.ENEMY_BLUE_BODY, outline="#FFFFFF", width=2
        )
        parts.append(body)
        # Red center eye
        eye = self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=self.ENEMY_RED_BODY, outline="#FF8888", width=2)
        parts.append(eye)
        # Side cannons
        cannon_l = self.canvas.create_rectangle(x - 22, y + 5, x - 15, y + 15, fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1)
        cannon_r = self.canvas.create_rectangle(x + 15, y + 5, x + 22, y + 15, fill=self.ENEMY_RED_BODY, outline="#FFFFFF", width=1)
        parts.extend([cannon_l, cannon_r])
        # Bottom thrusters
        for offset in [-8, 0, 8]:
            thruster = self.canvas.create_oval(
                x + offset - 3, y + 18, x + offset + 3, y + 25,
                fill="#FF6600", outline=""
            )
            parts.append(thruster)
        return parts
    
    def get_enemy_creator(self, enemy_type):
        """Return the appropriate enemy creation function"""
        creators = [
            self.create_enemy_purple_crab,
            self.create_enemy_red_scorpion,
            self.create_enemy_blue_butterfly,
            self.create_enemy_yellow_bee,
            self.create_enemy_red_white_bird,
            self.create_enemy_cyan_scorpion,
            self.create_enemy_green_bug,
            self.create_enemy_blue_dragonfly,
            self.create_enemy_blue_boss,
        ]
        return creators[enemy_type % len(creators)]
    
    def spawn_enemies(self):
        # Use different enemy types for variety
        formation = [
            [0, 1, 2, 3],      # Row 0: Various types
            [4, 5, 6, 7],      # Row 1: Various types
            [8, 0, 1, 2],      # Row 2: Boss type + others
            [3, 4, 5, 6],      # Row 3
            [7, 8, 0, 1],      # Row 4
        ]
        
        start_x = 80
        start_y = 60
        spacing_x = 60
        spacing_y = 50
        
        for row_idx, row in enumerate(formation):
            for col_idx, enemy_type in enumerate(row):
                x = start_x + col_idx * spacing_x
                y = start_y + row_idx * spacing_y
                
                creator = self.get_enemy_creator(enemy_type)
                parts = creator(x, y)
                
                self.enemies.append({
                    "parts": parts,
                    "x": x, "y": y,
                    "base_x": x,
                    "base_y": y,
                    "move_offset": random.random() * math.pi * 2,
                    "alive": True,
                    "type": enemy_type
                })
    
    def spawn_boss(self):
        """Spawn Galaga boss with burst fire pattern"""
        self.boss_mode = True
        self.boss_max_health = 60 + (self.level // 5) * 30
        self.boss_health = self.boss_max_health
        
        x = self.WIDTH // 2
        y = 120
        
        self.boss = {
            "parts": [],
            "x": x, "y": y,
            "base_x": x,
            "base_y": y,
            "move_offset": 0,
            "alive": True,
            "direction_y": 1,
            "target_y": y,
            # BURST FIRE PATTERN
            "shoot_timer": 0,
            "shoot_phase": "idle",  # idle, burst, cooldown
            "burst_count": 0,
            "burst_shots": 3,  # 3 shots per burst
            "burst_interval": 8,  # frames between burst shots
            "cooldown_duration": 120,  # frames to wait between bursts (2 seconds)
            "idle_duration": 60,  # frames before first burst
        }
        
        # Boss body - massive alien flagship
        body = self.canvas.create_polygon(
            x, y - 35,
            x - 15, y - 25,
            x - 25, y - 10,
            x - 30, y + 5,
            x - 25, y + 20,
            x - 15, y + 30,
            x - 5, y + 25,
            x, y + 35,
            x + 5, y + 25,
            x + 15, y + 30,
            x + 25, y + 20,
            x + 30, y + 5,
            x + 25, y - 10,
            x + 15, y - 25,
            fill=self.BOSS_COLOR, outline="#FF8888", width=3
        )
        self.boss["parts"].append(body)
        
        # Central eye
        eye = self.canvas.create_oval(
            x - 10, y - 12, x + 10, y + 8,
            fill="#FF0000", outline="#FFAA00", width=3
        )
        self.boss["parts"].append(eye)
        
        # Pupil
        pupil = self.canvas.create_oval(
            x - 4, y - 4, x + 4, y + 4,
            fill="#000000", outline=""
        )
        self.boss["parts"].append(pupil)
        
        # Side cannons
        cannon_l = self.canvas.create_rectangle(
            x - 28, y + 5, x - 18, y + 22,
            fill="#FF4400", outline="#FFFFFF", width=2
        )
        cannon_r = self.canvas.create_rectangle(
            x + 18, y + 5, x + 28, y + 22,
            fill="#FF4400", outline="#FFFFFF", width=2
        )
        self.boss["parts"].append(cannon_l)
        self.boss["parts"].append(cannon_r)
        
        # Top antennae
        ant_l = self.canvas.create_line(
            x - 10, y - 25, x - 15, y - 40,
            fill="#FF6600", width=3
        )
        ant_r = self.canvas.create_line(
            x + 10, y - 25, x + 15, y - 40,
            fill="#FF6600", width=3
        )
        self.boss["parts"].extend([ant_l, ant_r])
        
        # Engine flames
        for offset in [-12, 0, 12]:
            flame = self.canvas.create_oval(
                x + offset - 4, y + 30, x + offset + 4, y + 45,
                fill="#FF4400", outline="#FF8800", width=2
            )
            self.boss["parts"].append(flame)
        
        # Health bar
        self.boss_health_bg = self.canvas.create_rectangle(
            self.WIDTH // 2 - 100, 30, self.WIDTH // 2 + 100, 45,
            fill="#333333", outline="#FFFFFF", width=1
        )
        self.boss_health_bar = self.canvas.create_rectangle(
            self.WIDTH // 2 - 98, 32, self.WIDTH // 2 + 98, 43,
            fill="#FF0000", outline=""
        )
        
        self.canvas.create_text(
            self.WIDTH // 2, 55, text="★ ALIEN COMMANDER ★",
            fill="#FF8800", font=("Courier", 14, "bold")
        )
    
    def update_boss(self):
        """Update boss with burst fire pattern"""
        if not self.boss or not self.boss["alive"]:
            return
        
        # Movement - smooth oscillation
        self.boss["move_offset"] += 0.015
        new_x = self.WIDTH // 2 + math.sin(self.boss["move_offset"]) * 120
        y_offset = math.sin(self.boss["move_offset"] * 0.6) * 30
        new_y = 120 + y_offset
        
        # Clamp to keep in bounds
        new_x = max(80, min(self.WIDTH - 80, new_x))
        new_y = max(80, min(250, new_y))
        
        dx = new_x - self.boss["x"]
        dy = new_y - self.boss["y"]
        
        self.boss["x"] = new_x
        self.boss["y"] = new_y
        
        # Move all parts
        for part in self.boss["parts"]:
            coords = self.canvas.coords(part)
            if len(coords) >= 4:
                new_coords = []
                for i in range(0, len(coords), 2):
                    new_coords.append(coords[i] + dx)
                    new_coords.append(coords[i+1] + dy)
                self.canvas.coords(part, *new_coords)
        
        # === BURST FIRE PATTERN ===
        self.boss["shoot_timer"] += 1
        
        if self.boss["shoot_phase"] == "idle":
            # Waiting before first burst
            if self.boss["shoot_timer"] >= self.boss["idle_duration"]:
                self.boss["shoot_phase"] = "burst"
                self.boss["shoot_timer"] = 0
                self.boss["burst_count"] = 0
                
        elif self.boss["shoot_phase"] == "burst":
            # Firing burst shots
            if self.boss["shoot_timer"] >= self.boss["burst_interval"]:
                self.boss["shoot_timer"] = 0
                self.boss["burst_count"] += 1
                
                # Fire 3-way spread
                for angle in [-0.3, 0, 0.3]:
                    bx = self.boss["x"] + math.sin(angle) * 25
                    by = self.boss["y"] + 30
                    bullet = self.canvas.create_rectangle(
                        bx - 3, by, bx + 3, by + 14,
                        fill=self.ENEMY_BULLET_COLOR, outline="#FF8800", width=1
                    )
                    self.enemy_bullets.append({
                        "id": bullet, "x": bx, "y": by,
                        "dx": math.sin(angle) * 3, "dy": 5
                    })
                
                # Check if burst is complete
                if self.boss["burst_count"] >= self.boss["burst_shots"]:
                    self.boss["shoot_phase"] = "cooldown"
                    self.boss["shoot_timer"] = 0
                    
        elif self.boss["shoot_phase"] == "cooldown":
            # Resting between bursts
            if self.boss["shoot_timer"] >= self.boss["cooldown_duration"]:
                self.boss["shoot_phase"] = "burst"
                self.boss["shoot_timer"] = 0
                self.boss["burst_count"] = 0
    
    def update_boss_health_bar(self):
        if not self.boss_health_bar or not self.boss:
            return
        
        health_pct = max(0, self.boss_health / self.boss_max_health)
        bar_width = 196 * health_pct
        x_start = self.WIDTH // 2 - 98
        
        self.canvas.coords(self.boss_health_bar, x_start, 32, x_start + bar_width, 43)
        
        if health_pct > 0.5:
            color = "#00FF00"
        elif health_pct > 0.25:
            color = "#FFFF00"
        else:
            color = "#FF0000"
        self.canvas.itemconfig(self.boss_health_bar, fill=color)
    
    def key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)
    
    def key_release(self, event):
        key = event.keysym.lower()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
    
    def move_player(self, dx):
        if not self.game_running or self.paused:
            return
        
        self.player_x += dx
        self.player_x = max(25, min(self.WIDTH - 25, self.player_x))
        
        x, y = self.player_x, self.player_y
        
        if hasattr(self, 'player_body') and self.player_body:
            self.canvas.coords(self.player_body,
                x, y - 20,
                x - 5, y - 10,
                x - 8, y + 5,
                x - 12, y + 15,
                x - 20, y + 20,
                x - 8, y + 20,
                x - 3, y + 10,
                x, y + 15,
                x + 3, y + 10,
                x + 8, y + 20,
                x + 20, y + 20,
                x + 12, y + 15,
                x + 8, y + 5,
                x + 5, y - 10
            )
        
        if hasattr(self, 'player_wing_l') and self.player_wing_l:
            self.canvas.coords(self.player_wing_l,
                x - 12, y + 15,
                x - 20, y + 20,
                x - 8, y + 20
            )
        
        if hasattr(self, 'player_wing_r') and self.player_wing_r:
            self.canvas.coords(self.player_wing_r,
                x + 12, y + 15,
                x + 20, y + 20,
                x + 8, y + 20
            )
        
        if hasattr(self, 'player_cockpit') and self.player_cockpit:
            self.canvas.coords(self.player_cockpit,
                x - 3, y - 8, x + 3, y + 2
            )
        
        if hasattr(self, 'player_engine') and self.player_engine:
            self.canvas.coords(self.player_engine,
                x - 4, y + 15, x + 4, y + 25
            )
    
    def shoot(self, event=None):
        if not self.game_running or self.paused or self.invulnerable:
            return
        
        x = self.player_x
        y = self.player_y - 20
        
        bullet = self.canvas.create_rectangle(
            x - 2, y - 12, x + 2, y,
            fill=self.BULLET_COLOR, outline="#FFAA00", width=1
        )
        self.bullets.append({"id": bullet, "x": x, "y": y})
    
    def toggle_pause(self, event=None):
        if not self.game_running:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_text = self.canvas.create_text(
                self.WIDTH // 2, self.HEIGHT // 2,
                text="PAUSED", fill="#FFFF00",
                font=("Courier", 36, "bold")
            )
        else:
            if self.pause_text:
                self.canvas.delete(self.pause_text)
                self.pause_text = None
    
    def update_stars(self):
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] > self.HEIGHT:
                star["y"] = 0
                star["x"] = random.randint(0, self.WIDTH)
            self.canvas.coords(star["id"], 
                star["x"], star["y"], 
                star["x"] + 2, star["y"] + 2
            )
    
    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet["y"] -= self.BULLET_SPEED
            self.canvas.coords(bullet["id"],
                bullet["x"] - 2, bullet["y"] - 12,
                bullet["x"] + 2, bullet["y"]
            )
            
            if bullet["y"] < 0:
                self.canvas.delete(bullet["id"])
                self.bullets.remove(bullet)
        
        for bullet in self.enemy_bullets[:]:
            bullet["x"] += bullet.get("dx", 0)
            bullet["y"] += bullet.get("dy", self.BULLET_SPEED * 0.6)
            self.canvas.coords(bullet["id"],
                bullet["x"] - 2, bullet["y"],
                bullet["x"] + 2, bullet["y"] + 12
            )
            
            if bullet["y"] > self.HEIGHT or bullet["x"] < 0 or bullet["x"] > self.WIDTH:
                self.canvas.delete(bullet["id"])
                self.enemy_bullets.remove(bullet)
    
    def update_enemies(self):
        for enemy in self.enemies[:]:
            if not enemy["alive"]:
                continue
            
            enemy["move_offset"] += 0.025
            enemy["x"] = enemy["base_x"] + math.sin(enemy["move_offset"]) * 25
            enemy["y"] += 0.15
            
            x, y = enemy["x"], enemy["y"]
            
            for part in enemy["parts"]:
                coords = self.canvas.coords(part)
                if len(coords) >= 4:
                    cx = sum(coords[0::2]) / (len(coords) // 2)
                    cy = sum(coords[1::2]) / (len(coords) // 2)
                    dx = x - cx
                    dy = y - cy
                    
                    new_coords = []
                    for i in range(0, len(coords), 2):
                        new_coords.append(coords[i] + dx)
                        new_coords.append(coords[i+1] + dy)
                    self.canvas.coords(part, *new_coords)
            
            if random.random() < 0.0015 * self.level:
                bullet = self.canvas.create_rectangle(
                    x - 2, y + 10, x + 2, y + 22,
                    fill=self.ENEMY_BULLET_COLOR, outline=""
                )
                self.enemy_bullets.append({"id": bullet, "x": x, "y": y + 10, "dx": 0, "dy": 4})
            
            if enemy["y"] > self.HEIGHT - 50:
                self.game_over()
                return
    
    def check_collisions(self):
        if self.invulnerable:
            return
        
        # Player bullets vs Enemies
        for bullet in self.bullets[:]:
            bx, by = bullet["x"], bullet["y"]
            
            # Check vs regular enemies
            for enemy in self.enemies[:]:
                if not enemy["alive"]:
                    continue
                
                ex, ey = enemy["x"], enemy["y"]
                if (ex - 20 < bx < ex + 20 and ey - 20 < by < ey + 20):
                    enemy["alive"] = False
                    for part in enemy["parts"]:
                        self.canvas.delete(part)
                    self.enemies.remove(enemy)
                    
                    self.canvas.delete(bullet["id"])
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    self.create_explosion(ex, ey, "#FF4444")
                    self.score += 100 * self.level
                    self.update_ui()
                    
                    if not self.enemies:
                        self.level_up()
                    break
            
            # Check vs Boss
            if self.boss and self.boss["alive"]:
                bx_pos, by_pos = self.boss["x"], self.boss["y"]
                if (bx_pos - 55 < bx < bx_pos + 55 and by_pos - 45 < by < by_pos + 45):
                    self.boss_health -= 1
                    self.update_boss_health_bar()
                    
                    self.canvas.delete(bullet["id"])
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    
                    self.create_explosion(bx, by, "#FF6600")
                    
                    if self.boss_health <= 0:
                        self.defeat_boss()
                    break
        
        # Enemy bullets vs Player
        for bullet in self.enemy_bullets[:]:
            bx, by = bullet["x"], bullet["y"]
            px, py = self.player_x, self.player_y
            
            if (px - 18 < bx < px + 18 and py - 25 < by < py + 25):
                self.player_hit()
                self.canvas.delete(bullet["id"])
                self.enemy_bullets.remove(bullet)
                break
        
        # Enemies vs Player
        for enemy in self.enemies[:]:
            if not enemy["alive"]:
                continue
            ex, ey = enemy["x"], enemy["y"]
            px, py = self.player_x, self.player_y
            
            if (abs(px - ex) < 25 and abs(py - ey) < 25):
                self.player_hit()
                enemy["alive"] = False
                for part in enemy["parts"]:
                    self.canvas.delete(part)
                self.enemies.remove(enemy)
                self.create_explosion(ex, ey, "#FF0000")
                if not self.enemies:
                    self.level_up()
                break
        
        # Boss vs Player
        if self.boss and self.boss["alive"]:
            bx_pos, by_pos = self.boss["x"], self.boss["y"]
            px, py = self.player_x, self.player_y
            if (abs(px - bx_pos) < 50 and abs(py - by_pos) < 45):
                self.player_hit()
    
    def defeat_boss(self):
        if not self.boss:
            return
            
        self.boss["alive"] = False
        
        for _ in range(35):
            x = self.boss["x"] + random.randint(-60, 60)
            y = self.boss["y"] + random.randint(-50, 50)
            self.create_explosion(x, y, random.choice(["#FF0000", "#FF6600", "#FFCC00", "#FF4400", "#FF8800"]))
        
        for part in self.boss["parts"]:
            self.canvas.delete(part)
        
        self.boss = None
        self.boss_mode = False
        self.clear_boss_ui()
        
        self.score += 5000 * (self.level // 5)
        self.update_ui()
        
        self.show_you_win()
    
    def show_you_win(self):
        self.game_running = False
        
        if self.game_loop_id:
            self.root.after_cancel(self.game_loop_id)
            self.game_loop_id = None
        
        parts = ['player_body', 'player_wing_l', 'player_wing_r', 'player_cockpit', 'player_engine']
        for part in parts:
            if hasattr(self, part):
                p = getattr(self, part)
                if p:
                    self.canvas.delete(p)
                    setattr(self, part, None)
        
        self.clear_bullets()
        self.clear_enemies()
        self.clear_particles()
        self.clear_all_texts()
        self.clear_boss_ui()
        
        self.you_win_text = self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 3 - 20,
            text="YOU WIN!", fill="#00FF00",
            font=("Courier", 48, "bold")
        )
        self.you_win_subtext = self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 2,
            text=f"Alien Commander Defeated!\nScore: {self.score:05d}\nLevel: {self.level}\n\nPUSH START BUTTON",
            fill="#FFFFFF", font=("Courier", 18)
        )
    
    def create_explosion(self, x, y, color):
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            size = random.randint(2, 5)
            particle = self.canvas.create_oval(
                x, y, x + size, y + size,
                fill=color, outline=""
            )
            self.particles.append({
                "id": particle,
                "x": x, "y": y,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "life": 15
            })
    
    def update_particles(self):
        for particle in self.particles[:]:
            particle["x"] += particle["dx"]
            particle["y"] += particle["dy"]
            particle["life"] -= 1
            
            self.canvas.coords(particle["id"],
                particle["x"], particle["y"],
                particle["x"] + 4, particle["y"] + 4
            )
            
            if particle["life"] <= 0:
                self.canvas.delete(particle["id"])
                self.particles.remove(particle)
    
    def player_hit(self):
        if self.invulnerable or not self.game_running:
            return
        
        self.lives -= 1
        self.update_ui()
        self.create_explosion(self.player_x, self.player_y, "#00FF00")
        
        flash = self.canvas.create_rectangle(
            0, 0, self.WIDTH, self.HEIGHT,
            fill="red", stipple="gray50"
        )
        self.root.after(100, lambda: self.canvas.delete(flash))
        
        if self.lives <= 0:
            self.game_over()
        else:
            self.invulnerable = True
            parts = ['player_body', 'player_wing_l', 'player_wing_r', 'player_cockpit', 'player_engine']
            for part in parts:
                if hasattr(self, part):
                    p = getattr(self, part)
                    if p:
                        self.canvas.itemconfig(p, state="hidden")
            
            self.root.after(1500, self.respawn_player)
    
    def respawn_player(self):
        if not self.game_running:
            return
        
        self.player_x = self.WIDTH // 2
        self.player_y = self.HEIGHT - 80
        
        parts = ['player_body', 'player_wing_l', 'player_wing_r', 'player_cockpit', 'player_engine']
        for part in parts:
            if hasattr(self, part):
                p = getattr(self, part)
                if p:
                    self.canvas.delete(p)
        
        self.create_player()
        self.root.after(1000, self.end_invulnerability)
    
    def end_invulnerability(self):
        self.invulnerable = False
    
    def level_up(self):
        self.level += 1
        self.update_ui()
        
        self.clear_bullets()
        
        if self.level_text_display:
            self.canvas.delete(self.level_text_display)
        
        if self.level % self.BOSS_LEVEL == 0:
            self.level_text_display = self.canvas.create_text(
                self.WIDTH // 2, self.HEIGHT // 2,
                text=f"BOSS LEVEL {self.level}", fill="#FF8800",
                font=("Courier", 32, "bold")
            )
            self.root.after(3000, lambda: (
                self.canvas.delete(self.level_text_display) if self.level_text_display else None,
                setattr(self, 'level_text_display', None),
                self.spawn_boss()
            ))
        else:
            self.level_text_display = self.canvas.create_text(
                self.WIDTH // 2, self.HEIGHT // 2,
                text=f"LEVEL {self.level}", fill="#00FF00",
                font=("Courier", 36, "bold")
            )
            self.root.after(2000, lambda: (
                self.canvas.delete(self.level_text_display) if self.level_text_display else None,
                setattr(self, 'level_text_display', None),
                self.spawn_enemies()
            ))
    
    def update_ui(self):
        self.canvas.itemconfig(self.score_text, text=f"{self.score:05d}")
        self.canvas.itemconfig(self.lives_text, text=f"{self.lives}")
        if self.score > self.high_score:
            self.high_score = self.score
            self.canvas.itemconfig(self.high_text, text=f"{self.high_score:05d}")
    
    def game_over(self):
        self.game_running = False
        self.invulnerable = False
        self.boss_mode = False
        
        if self.game_loop_id:
            self.root.after_cancel(self.game_loop_id)
            self.game_loop_id = None
        
        if self.boss:
            for part in self.boss["parts"]:
                self.canvas.delete(part)
            self.boss = None
            self.clear_boss_ui()
        
        parts = ['player_body', 'player_wing_l', 'player_wing_r', 'player_cockpit', 'player_engine']
        for part in parts:
            if hasattr(self, part):
                p = getattr(self, part)
                if p:
                    self.canvas.delete(p)
                    setattr(self, part, None)
        
        self.clear_bullets()
        self.clear_enemies()
        self.clear_particles()
        self.clear_all_texts()
        
        self.game_over_text = self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 3 - 20,
            text="GAME OVER", fill="#FF0000",
            font=("Courier", 48, "bold")
        )
        self.game_over_subtext = self.canvas.create_text(
            self.WIDTH // 2, self.HEIGHT // 2,
            text=f"Score: {self.score:05d}\nLevel: {self.level}\n\nPUSH START BUTTON",
            fill="#FFFFFF", font=("Courier", 18)
        )
    
    def game_loop(self):
        if not self.game_running:
            return
        
        if not self.paused:
            if 'left' in self.keys_pressed or 'a' in self.keys_pressed:
                self.player_vel_x = -self.PLAYER_SPEED
            elif 'right' in self.keys_pressed or 'd' in self.keys_pressed:
                self.player_vel_x = self.PLAYER_SPEED
            else:
                self.player_vel_x = 0
            
            if self.player_vel_x != 0:
                self.move_player(self.player_vel_x)
            
            self.update_stars()
            self.update_bullets()
            
            if self.boss_mode and self.boss and self.boss["alive"]:
                self.update_boss()
                self.update_boss_health_bar()
            elif self.boss_mode and not self.boss:
                self.boss_mode = False
            
            if not self.boss_mode:
                self.update_enemies()
            
            self.check_collisions()
            self.update_particles()
        
        self.game_loop_id = self.root.after(16, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = GalagaGame(root)
    root.mainloop()