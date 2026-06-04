#nullable enable
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace ElevatorSim
{
    public partial class ElevatorForm : Form
    {
        private readonly Elevator _elevator;
        private const int TotalFloors = 4;

        // ── Logical state ─────────────────────────────────────────────────
        private int _currentFloor = 1;
        private ElevatorDirection _dir = ElevatorDirection.Idle;
        private bool _systemRunning = true;

        // ── Door state ────────────────────────────────────────────────────
        private bool _doorsOpen = false;
        private float _doorOpenPct = 0f;
        private bool _pendingDoorOpen = false;
        private bool _pendingDoorClose = false;
        private readonly System.Windows.Forms.Timer _doorAnimTimer;

        // ── Smooth car movement ───────────────────────────────────────────
        private float _carY = 0f;
        private float _targetCarY = 0f;
        private bool _carYInitialised = false;
        private readonly System.Windows.Forms.Timer _renderTimer;

        public ElevatorForm()
        {
            InitializeComponent();
            _elevator = new Elevator(TotalFloors);
            SubscribeToElevatorEvents();

            _doorAnimTimer = new System.Windows.Forms.Timer { Interval = 16 };
            _doorAnimTimer.Tick += DoorAnimTick;

            _renderTimer = new System.Windows.Forms.Timer { Interval = 16 };
            _renderTimer.Tick += RenderTick;
            _renderTimer.Start();
        }

        private const float CarSpeedPxPerFrame = 3.5f;
        private const float EaseZone = 60f;

        private void RenderTick(object? sender, EventArgs e)
        {
            if (!_carYInitialised) return;

            float diff = _targetCarY - _carY;
            float absDiff = Math.Abs(diff);

            if (absDiff > 0.8f)
            {
                float move;
                if (absDiff > EaseZone)
                {
                    move = CarSpeedPxPerFrame * Math.Sign(diff);
                    if (Math.Abs(move) > absDiff - EaseZone)
                        move = (absDiff - EaseZone) * Math.Sign(diff);
                }
                else
                {
                    move = diff * 0.07f;
                    if (Math.Abs(move) < 0.8f)
                        move = 0.8f * Math.Sign(diff);
                }

                _carY += move;
                GetShaftPanel()?.Invalidate();
            }
            else
            {
                if (absDiff > 0f)
                {
                    _carY = _targetCarY;
                    GetShaftPanel()?.Invalidate();
                }

                if (_pendingDoorOpen)
                {
                    _pendingDoorOpen = false;
                    _doorsOpen = true;
                    _doorAnimTimer.Start();
                    UpdateStatusLabels();
                }
                else if (_pendingDoorClose)
                {
                    _pendingDoorClose = false;
                    _doorsOpen = false;
                    _doorAnimTimer.Start();
                    UpdateStatusLabels();
                }
            }
        }

        private void DoorAnimTick(object? sender, EventArgs e)
        {
            const float step = 0.045f;
            bool done;
            if (_doorsOpen && _doorOpenPct < 1f)
            {
                _doorOpenPct = Math.Min(1f, _doorOpenPct + step);
                done = _doorOpenPct >= 1f;
            }
            else if (!_doorsOpen && _doorOpenPct > 0f)
            {
                _doorOpenPct = Math.Max(0f, _doorOpenPct - step);
                done = _doorOpenPct <= 0f;
            }
            else { done = true; }

            UpdateStatusLabels();
            GetShaftPanel()?.Invalidate();
            if (done) _doorAnimTimer.Stop();
        }

        private void UpdateTargetCarY()
        {
            var panel = GetShaftPanel();
            if (panel == null) return;
            int H = panel.Height;
            int floorH = (H - 36 - 4) / TotalFloors;
            int carH = (int)(floorH * 0.82f);
            int yBase = 36 + (TotalFloors - _currentFloor) * floorH;
            _targetCarY = yBase + (floorH - carH) / 2f;
            if (!_carYInitialised) { _carY = _targetCarY; _carYInitialised = true; }
        }

        private void SubscribeToElevatorEvents()
        {
            _elevator.FloorChanged += (_, e) => this.Invoke(() =>
            {
                _currentFloor = e.CurrentFloor;
                var d = GetCurrentFloorDisplay();
                if (d != null) d.Text = e.CurrentFloor.ToString();
                UpdateTargetCarY();
                UpdateStatusLabels();
            });

            _elevator.DirectionChanged += (_, e) => this.Invoke(() =>
            {
                _dir = e.Direction;
                UpdateStatusLabels();
            });

            _elevator.RequestAdded += (_, e) => this.Invoke(() =>
                HighlightFloorBtn(e.CurrentFloor, true));

            _elevator.ElevatorStopped += (_, _) => this.Invoke(UpdateStatusLabels);

            _elevator.DoorsOpened += (_, e) => this.Invoke(() =>
            {
                _pendingDoorOpen = true;
                _pendingDoorClose = false;
                HighlightFloorBtn(e.CurrentFloor, false);
                UpdateStatusLabels();
            });

            _elevator.DoorsClosed += (_, _) => this.Invoke(() =>
            {
                _pendingDoorClose = true;
                _pendingDoorOpen = false;
                UpdateStatusLabels();
            });
        }

        private void UpdateStatusLabels()
        {
            var dir = GetStatusDirectionLabel();
            var door = GetStatusDoorLabel();

            if (dir != null)
                dir.Text = _dir switch
                {
                    ElevatorDirection.Up => "DIRECTION   ↑  UP",
                    ElevatorDirection.Down => "DIRECTION   ↓  DOWN",
                    _ => "DIRECTION   —  IDLE"
                };

            if (door != null)
            {
                bool opening = _pendingDoorOpen || (_doorsOpen && _doorOpenPct < 1f);
                bool closing = _pendingDoorClose || (!_doorsOpen && _doorOpenPct > 0f);

                if (opening) door.Text = $"DOOR STATUS   OPENING {(int)(_doorOpenPct * 100)}%";
                else if (_doorsOpen) door.Text = "DOOR STATUS   OPEN";
                else if (closing) door.Text = $"DOOR STATUS   CLOSING {(int)((1 - _doorOpenPct) * 100)}%";
                else door.Text = "DOOR STATUS   CLOSED";
            }

            bool idle = _dir == ElevatorDirection.Idle;
            bool carArrived = Math.Abs(_targetCarY - _carY) < 1f;
            GetOpenDoorButton()!.Enabled = _systemRunning && idle && !_doorsOpen && !_pendingDoorOpen && carArrived;
            GetCloseDoorButton()!.Enabled = _systemRunning && (_doorsOpen || _pendingDoorOpen);
            GetUpButton()!.Enabled = _systemRunning && idle && !_doorsOpen && carArrived && _currentFloor < TotalFloors;
            GetDownButton()!.Enabled = _systemRunning && idle && !_doorsOpen && carArrived && _currentFloor > 1;
        }

        private void HighlightFloorBtn(int floor, bool on)
        {
            var btns = GetFloorButtons();
            if (btns == null || floor < 1 || floor > TotalFloors) return;
            btns[floor - 1].BackColor = on
                ? Color.FromArgb(220, 140, 0)       // amber lit
                : Color.FromArgb(52, 38, 10);        // amber dark (off)
        }

        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);

            LayoutFloorButtons();
            ForceLayoutLcd();
            UpdateTargetCarY();

            var btns = GetFloorButtons();
            if (btns != null)
                foreach (var btn in btns)
                    btn.Click += (s, _) => { if (s is Button b && b.Tag is int f) _elevator.RequestFloor(f); };

            GetOpenDoorButton()!.Click += (_, _) => _elevator.ManualOpenDoors();
            GetCloseDoorButton()!.Click += (_, _) => _elevator.ManualCloseDoors();
            GetUpButton()!.Click += (_, _) => _elevator.MoveUp();
            GetDownButton()!.Click += (_, _) => _elevator.MoveDown();

            GetStartButton()!.Click += (_, _) =>
            {
                _systemRunning = true;
                _elevator.Resume();
                GetPauseButton()!.Text = "⏸  PAUSE";
                SetInputEnabled(true);
                UpdateStatusLabels();
            };
            GetPauseButton()!.Click += (_, _) =>
            {
                _systemRunning = !_systemRunning;
                if (_systemRunning)
                {
                    _elevator.Resume();
                    GetPauseButton()!.Text = "⏸  PAUSE";
                }
                else
                {
                    _elevator.Pause();
                    GetPauseButton()!.Text = "▶  RESUME";
                }
                SetInputEnabled(_systemRunning);
                UpdateStatusLabels();
            };
            GetStopButton()!.Click += (_, _) =>
            {
                _elevator.Pause();
                _systemRunning = false;
                _doorsOpen = false;
                _doorOpenPct = 0f;
                _pendingDoorOpen = false;
                _pendingDoorClose = false;
                _dir = ElevatorDirection.Idle;
                _doorAnimTimer.Stop();
                var fb = GetFloorButtons();
                if (fb != null) foreach (var b in fb) b.BackColor = Color.FromArgb(52, 38, 10);
                SetInputEnabled(false);
                GetShaftPanel()?.Invalidate();
                UpdateStatusLabels();
            };

            GetShaftPanel()!.Paint += (_, pe) => DrawShaft(pe.Graphics);
            GetShaftPanel()!.Resize += (_, _) => { _carYInitialised = false; UpdateTargetCarY(); };

            UpdateStatusLabels();
        }

        private void SetInputEnabled(bool en)
        {
            var btns = GetFloorButtons();
            if (btns != null) foreach (var b in btns) b.Enabled = en;
        }

        // ═══════════════════════════════════════════════════════════════
        // SHAFT DRAWING — Midnight Amber theme
        // ═══════════════════════════════════════════════════════════════
        private void DrawShaft(Graphics g)
        {
            var panel = GetShaftPanel();
            if (panel == null) return;
            int W = panel.Width, H = panel.Height;

            g.SmoothingMode = SmoothingMode.AntiAlias;
            g.PixelOffsetMode = PixelOffsetMode.HighQuality;
            g.Clear(Color.FromArgb(22, 24, 30));   // near-black charcoal

            using var titleFont = new Font("Arial", 13, FontStyle.Bold);
            g.DrawString("4-Story Building", titleFont,
                new SolidBrush(Color.FromArgb(200, 150, 30)), 10, 6);

            const int topOffset = 36, botPad = 4;
            int totalH = H - topOffset - botPad;
            int floorH = totalH / TotalFloors;
            int shaftW = Math.Max(80, (int)(W * 0.22f));
            int shaftLeft = (int)(W * 0.44f);
            int shaftRight = shaftLeft + shaftW;

            for (int floor = TotalFloors; floor >= 1; floor--)
            {
                int yTop = topOffset + (TotalFloors - floor) * floorH;
                g.DrawLine(new Pen(Color.FromArgb(55, 58, 68), 2), 0, yTop, W, yTop);

                using var bgBrush = new SolidBrush(Color.FromArgb(30, 28, 22));
                g.FillRectangle(bgBrush, 0, yTop + 1, shaftLeft, floorH - 2);
                g.FillRectangle(bgBrush, shaftRight, yTop + 1, W - shaftRight, floorH - 2);

                DrawFloorLabel(g, floor, 55, yTop, floorH);
                DrawLeftCorridor(g, shaftLeft, yTop, floorH);
                DrawRightCorridor(g, shaftRight, yTop, W, floorH, floor);
            }
            g.DrawLine(new Pen(Color.FromArgb(55, 58, 68), 2), 0, topOffset + totalH, W, topOffset + totalH);

            // Shaft walls + rails
            g.DrawLine(new Pen(Color.FromArgb(12, 14, 20), 3), shaftLeft, topOffset, shaftLeft, topOffset + totalH);
            g.DrawLine(new Pen(Color.FromArgb(12, 14, 20), 3), shaftRight, topOffset, shaftRight, topOffset + totalH);
            g.DrawLine(new Pen(Color.FromArgb(75, 65, 30), 2), shaftLeft + 7, topOffset, shaftLeft + 7, topOffset + totalH);
            g.DrawLine(new Pen(Color.FromArgb(75, 65, 30), 2), shaftRight - 7, topOffset, shaftRight - 7, topOffset + totalH);

            int carW = shaftW - 18;
            int carH = (int)(floorH * 0.82f);
            DrawCar(g, shaftLeft + 9, (int)_carY, carW, carH);
        }

        private static void DrawFloorLabel(Graphics g, int floor, int labelAreaW,
            int yTop, int floorH)
        {
            using var f1 = new Font("Arial", 8, FontStyle.Bold);
            using var f2 = new Font("Arial", 18, FontStyle.Bold);

            string word = "FLOOR";
            string num = floor.ToString();

            SizeF wSize = g.MeasureString(word, f1);
            SizeF nSize = g.MeasureString(num, f2);

            int totalH = (int)(wSize.Height + nSize.Height);
            int startY = yTop + (floorH - totalH) / 2;

            float wordX = (labelAreaW - wSize.Width) / 2f;
            float numX = (labelAreaW - nSize.Width) / 2f;

            g.DrawString(word, f1, new SolidBrush(Color.FromArgb(160, 140, 80)), wordX, startY);
            g.DrawString(num, f2, new SolidBrush(Color.FromArgb(210, 170, 50)), numX, startY + wSize.Height);
        }

        private static void DrawLeftCorridor(Graphics g, int shaftLeft, int yTop, int floorH)
        {
            int lEdge = 55, rEdge = shaftLeft - 4;
            g.FillRectangle(new SolidBrush(Color.FromArgb(38, 34, 26)), lEdge, yTop + 2, rEdge - lEdge, floorH - 4);

            // ceiling light strip — warm amber
            int lx = lEdge + (rEdge - lEdge) / 2 + 28, ly = yTop + 5;
            g.FillRectangle(new SolidBrush(Color.FromArgb(255, 200, 80)), lx, ly, 20, 5);
            g.DrawRectangle(new Pen(Color.FromArgb(160, 120, 20), 1), lx, ly, 19, 4);

            // door
            int dW = 46, dH = (int)(floorH * 0.60f);
            int dX = rEdge - dW - 10, dY = yTop + floorH - dH - 2;
            g.FillRectangle(new SolidBrush(Color.FromArgb(80, 55, 22)), dX, dY, dW, dH);
            var dPen = new Pen(Color.FromArgb(40, 28, 8), 1);
            g.DrawRectangle(dPen, dX, dY, dW - 1, dH - 1);
            g.DrawLine(dPen, dX + dW / 2, dY + 3, dX + dW / 2, dY + dH - 3);
            g.DrawLine(dPen, dX + 3, dY + dH / 2, dX + dW - 4, dY + dH / 2);
            g.FillEllipse(new SolidBrush(Color.FromArgb(200, 160, 40)), dX + dW - 9, dY + dH / 2 - 3, 6, 6);

            // plant
            int px = lEdge + 8, pyB = yTop + floorH - 2;
            g.FillRectangle(new SolidBrush(Color.FromArgb(100, 65, 20)), px, pyB - 12, 12, 10);
            g.FillEllipse(new SolidBrush(Color.FromArgb(28, 95, 28)), px - 5, pyB - 26, 22, 18);
            g.FillEllipse(new SolidBrush(Color.FromArgb(20, 72, 20)), px, pyB - 32, 14, 14);
        }

        private void DrawRightCorridor(Graphics g, int shaftRight, int yTop, int W, int floorH, int floor)
        {
            int lx = W - 30, ly = yTop + 6;
            g.FillRectangle(new SolidBrush(Color.FromArgb(255, 200, 80)), lx, ly, 16, 5);
            g.DrawRectangle(new Pen(Color.FromArgb(160, 120, 20), 1), lx, ly, 15, 4);
            DrawCallPanel(g, shaftRight + 6, yTop + floorH / 2 - 28, floor, _currentFloor, _dir);
        }

        private static void DrawCallPanel(Graphics g, int x, int y, int floor,
            int elevatorFloor, ElevatorDirection elevatorDir)
        {
            int panW = 30, btnH = 24, gap = 3;
            bool hasUp = floor < TotalFloors;
            bool hasDown = floor > 1;
            int panH = 6 + (hasUp ? btnH : 0) + (hasUp && hasDown ? gap : 0) + (hasDown ? btnH : 0);
            panH = Math.Max(panH, 28);

            g.FillRectangle(new SolidBrush(Color.FromArgb(40, 36, 24)), x, y, panW, panH);
            var pp = new Pen(Color.FromArgb(80, 65, 20), 1);
            g.DrawRectangle(pp, x, y, panW - 1, panH - 1);

            using var af = new Font("Arial", 8, FontStyle.Bold);

            bool upLit = hasUp && floor == elevatorFloor && elevatorDir == ElevatorDirection.Up;
            bool downLit = hasDown && floor == elevatorFloor && elevatorDir == ElevatorDirection.Down;

            int btnY = y + 3;
            if (hasUp)
            {
                var fill = upLit
                    ? new SolidBrush(Color.FromArgb(230, 150, 0))
                    : new SolidBrush(Color.FromArgb(58, 50, 24));
                var arrow = upLit
                    ? new SolidBrush(Color.FromArgb(20, 14, 0))
                    : new SolidBrush(Color.FromArgb(140, 110, 40));
                g.FillRectangle(fill, x + 3, btnY, panW - 6, btnH);
                g.DrawRectangle(pp, x + 3, btnY, panW - 7, btnH - 1);
                g.DrawString("▲", af, arrow, x + 8, btnY + 4);
                btnY += btnH + gap;
            }
            if (hasDown)
            {
                var fill = downLit
                    ? new SolidBrush(Color.FromArgb(230, 150, 0))
                    : new SolidBrush(Color.FromArgb(58, 50, 24));
                var arrow = downLit
                    ? new SolidBrush(Color.FromArgb(20, 14, 0))
                    : new SolidBrush(Color.FromArgb(140, 110, 40));
                g.FillRectangle(fill, x + 3, btnY, panW - 6, btnH);
                g.DrawRectangle(pp, x + 3, btnY, panW - 7, btnH - 1);
                g.DrawString("▼", af, arrow, x + 8, btnY + 4);
            }
        }

        private void DrawCar(Graphics g, int x, int y, int w, int h)
        {
            // Drop shadow
            g.FillRectangle(new SolidBrush(Color.FromArgb(40, 0, 0, 0)), x + 4, y + 4, w, h);
            // Car body — dark steel
            g.FillRectangle(new SolidBrush(Color.FromArgb(48, 52, 62)), x, y, w, h);
            g.DrawRectangle(new Pen(Color.FromArgb(90, 75, 25), 2), x, y, w, h);

            // Display panel — black with amber glow
            int dispH = Math.Max(20, h / 4);
            g.FillRectangle(new SolidBrush(Color.FromArgb(10, 8, 2)), x + 2, y + 2, w - 4, dispH);

            using var numFont = new Font("Courier New", 12, FontStyle.Bold);
            using var numBrush = new SolidBrush(Color.FromArgb(255, 160, 20));
            string numTxt = _currentFloor.ToString();
            SizeF ns = g.MeasureString(numTxt, numFont);
            g.DrawString(numTxt, numFont, numBrush,
                x + (w - ns.Width) / 2, y + 2 + (dispH - ns.Height) / 2);

            if (_dir != ElevatorDirection.Idle)
                g.DrawString(_dir == ElevatorDirection.Up ? "▲" : "▼",
                    new Font("Arial", 8, FontStyle.Bold),
                    new SolidBrush(Color.FromArgb(255, 160, 20)),
                    x + w - 14, y + 4);

            DrawDoors(g, x, y + dispH + 2, w, h - dispH - 4);
        }

        private void DrawDoors(Graphics g, int cx, int cy, int cw, int ch)
        {
            int halfW = cw / 2, singleW = halfW - 1;
            int offset = (int)(singleW * _doorOpenPct);

            if (offset > 0)
            {
                // Interior visible when open — warm amber glow
                g.FillRectangle(new SolidBrush(Color.FromArgb(12, 10, 4)), cx + 2, cy, cw - 4, ch);
                g.FillRectangle(new SolidBrush(Color.FromArgb(22, 255, 190, 80)), cx + cw / 4, cy, cw / 2, ch);
                int lx = cx + 2 - offset, rx = cx + halfW + offset;
                g.FillRectangle(new SolidBrush(Color.FromArgb(62, 58, 44)), lx, cy, singleW, ch);
                DoorDetail(g, lx, cy, singleW, ch, true);
                g.FillRectangle(new SolidBrush(Color.FromArgb(62, 58, 44)), rx, cy, singleW, ch);
                DoorDetail(g, rx, cy, singleW, ch, false);
            }
            else
            {
                g.FillRectangle(new SolidBrush(Color.FromArgb(62, 58, 44)), cx + 2, cy, cw - 4, ch);
                g.DrawLine(new Pen(Color.FromArgb(35, 30, 15), 2), cx + halfW, cy, cx + halfW, cy + ch);
                int my = cy + ch / 2;
                g.FillEllipse(new SolidBrush(Color.FromArgb(180, 140, 50)), cx + halfW - 9, my - 3, 7, 7);
                g.FillEllipse(new SolidBrush(Color.FromArgb(180, 140, 50)), cx + halfW + 2, my - 3, 7, 7);
            }
        }

        private static void DoorDetail(Graphics g, int x, int y, int w, int h, bool isLeft)
        {
            g.DrawRectangle(new Pen(Color.FromArgb(90, 80, 50), 1), x, y, w - 1, h - 1);
            int hx = isLeft ? x + w - 8 : x + 6;
            g.FillEllipse(new SolidBrush(Color.FromArgb(180, 140, 50)), hx - 3, y + h / 2 - 3, 7, 7);
        }

        private void ForceLayoutLcd()
        {
            var lcd = GetLcdContentPanel();
            if (lcd == null) return;
            lcd.PerformLayout();
            int w = lcd.ClientSize.Width;
            int h = lcd.ClientSize.Height;
            if (w <= 0 || h <= 0) return;

            int y = 4;
            int capH = Math.Max(16, (int)(h * 0.12f));
            int numH = Math.Max(50, (int)(h * 0.46f));
            int rowH = Math.Max(18, (int)(h * 0.17f));

            var cap = GetCurrentFloorDisplay();
            var dir = GetStatusDirectionLabel();
            var door = GetStatusDoorLabel();

            if (lcd.Controls.Count >= 4)
            {
                lcd.Controls[0].SetBounds(0, y, w, capH); y += capH + 2;
                cap?.SetBounds(0, y, w, numH); y += numH + 4;
                dir?.SetBounds(0, y, w, rowH); y += rowH + 2;
                door?.SetBounds(0, y, w, rowH);
            }
        }

        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            base.OnFormClosed(e);
            _doorAnimTimer.Stop(); _doorAnimTimer.Dispose();
            _renderTimer.Stop(); _renderTimer.Dispose();
        }
    }
}