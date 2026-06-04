#nullable enable
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Windows.Forms;

namespace ElevatorSim
{
    partial class ElevatorForm
    {
        private System.ComponentModel.IContainer? components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing) components?.Dispose();
            base.Dispose(disposing);
        }

        // Double-buffered panel — eliminates all flicker
        private sealed class DBPanel : Panel
        {
            public DBPanel() { DoubleBuffered = true; ResizeRedraw = true; }
        }

        private void InitializeComponent()
        {
            components = new System.ComponentModel.Container();

            Text = "Elevator Control System";
            Size = new Size(1280, 760);
            MinimumSize = new Size(1100, 660);
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(18, 19, 24);  // deep charcoal

            var root = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.FromArgb(18, 19, 24),
                Padding = new Padding(6)
            };
            Controls.Add(root);

            // ── Main 60/40 split ──────────────────────────────────────────
            var mainSplit = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 2,
                RowCount = 1,
                BackColor = Color.Transparent
            };
            mainSplit.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 60f));
            mainSplit.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 40f));
            mainSplit.RowStyles.Add(new RowStyle(SizeType.Percent, 100f));
            root.Controls.Add(mainSplit);

            // ── LEFT: shaft (double-buffered, no flicker) ─────────────────
            ShaftPanel = new DBPanel
            {
                BackColor = Color.FromArgb(22, 24, 30),
                BorderStyle = BorderStyle.FixedSingle,
                Dock = DockStyle.Fill,
                Margin = new Padding(0, 0, 4, 0)
            };
            ShaftPanel.Paint += ShaftPanel_Paint;
            mainSplit.Controls.Add(ShaftPanel, 0, 0);

            // ── RIGHT: 3-row layout ───────────────────────────────────────
            var rightOuter = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 1,
                RowCount = 3,
                BackColor = Color.Transparent,
                Margin = new Padding(4, 0, 0, 0)
            };
            rightOuter.RowStyles.Add(new RowStyle(SizeType.Percent, 57f));
            rightOuter.RowStyles.Add(new RowStyle(SizeType.Percent, 25f));
            rightOuter.RowStyles.Add(new RowStyle(SizeType.Percent, 18f));
            rightOuter.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100f));
            mainSplit.Controls.Add(rightOuter, 1, 0);

            // ── Row 0: Status LCD (left 62%) + Floor selection (right 38%) ─
            var row0 = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 2,
                RowCount = 1,
                BackColor = Color.Transparent,
                Margin = new Padding(0, 0, 0, 4)
            };
            row0.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 62f));
            row0.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 38f));
            row0.RowStyles.Add(new RowStyle(SizeType.Percent, 100f));
            rightOuter.Controls.Add(row0, 0, 0);

            // ── Status LCD ────────────────────────────────────────────────
            var statusPanel = new Panel
            {
                BackColor = Color.FromArgb(8, 8, 10),   // near-black LCD
                Dock = DockStyle.Fill,
                Margin = new Padding(0, 0, 3, 0),
                Padding = new Padding(0)
            };
            row0.Controls.Add(statusPanel, 0, 0);

            var statusHeader = new Label
            {
                Text = "ELEVATOR STATUS",
                Font = new Font("Courier New", 11, FontStyle.Bold),
                ForeColor = Color.FromArgb(200, 155, 20),   // amber
                BackColor = Color.FromArgb(22, 18, 4),      // dark amber header
                Dock = DockStyle.Top,
                Height = 32,
                TextAlign = ContentAlignment.MiddleCenter
            };
            statusPanel.Controls.Add(statusHeader);

            LcdContentPanel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.Transparent
            };
            statusPanel.Controls.Add(LcdContentPanel);
            var lcdContent = LcdContentPanel;

            var cfCaption = new Label
            {
                Text = "CURRENT FLOOR",
                Font = new Font("Courier New", 9, FontStyle.Bold),
                ForeColor = Color.FromArgb(255, 160, 20),   // amber glow
                BackColor = Color.Transparent,
                TextAlign = ContentAlignment.MiddleCenter,
                Dock = DockStyle.None
            };
            lcdContent.Controls.Add(cfCaption);

            CurrentFloorDisplay = new Label
            {
                Text = "1",
                Font = new Font("Courier New", 58, FontStyle.Bold),
                ForeColor = Color.FromArgb(255, 160, 20),   // amber glow
                BackColor = Color.Transparent,
                TextAlign = ContentAlignment.MiddleCenter,
                Dock = DockStyle.None
            };
            lcdContent.Controls.Add(CurrentFloorDisplay);

            StatusDirectionLabel = new Label
            {
                Text = "DIRECTION   —  IDLE",
                Font = new Font("Courier New", 9, FontStyle.Bold),
                ForeColor = Color.FromArgb(200, 130, 15),   // dimmer amber
                BackColor = Color.Transparent,
                TextAlign = ContentAlignment.MiddleCenter,
                Dock = DockStyle.None
            };
            lcdContent.Controls.Add(StatusDirectionLabel);

            StatusDoorLabel = new Label
            {
                Text = "DOOR STATUS   CLOSED",
                Font = new Font("Courier New", 9, FontStyle.Bold),
                ForeColor = Color.FromArgb(200, 130, 15),   // dimmer amber
                BackColor = Color.Transparent,
                TextAlign = ContentAlignment.MiddleCenter,
                Dock = DockStyle.None
            };
            lcdContent.Controls.Add(StatusDoorLabel);

            void LayoutLcd()
            {
                int w = lcdContent.ClientSize.Width;
                int h = lcdContent.ClientSize.Height;
                if (w <= 0 || h <= 0) return;

                int y = 4;
                int capH = Math.Max(16, (int)(h * 0.12f));
                int numH = Math.Max(50, (int)(h * 0.46f));
                int rowH = Math.Max(18, (int)(h * 0.17f));

                cfCaption.SetBounds(0, y, w, capH); y += capH + 2;
                CurrentFloorDisplay!.SetBounds(0, y, w, numH); y += numH + 4;
                StatusDirectionLabel!.SetBounds(0, y, w, rowH); y += rowH + 2;
                StatusDoorLabel!.SetBounds(0, y, w, rowH);
            }
            lcdContent.Resize += (_, _) => LayoutLcd();
            statusPanel.VisibleChanged += (_, _) => { if (statusPanel.Visible) LayoutLcd(); };

            // ── Floor selection ───────────────────────────────────────────
            var floorSelPanel = new Panel
            {
                BackColor = Color.FromArgb(14, 12, 6),  // very dark amber-black
                Dock = DockStyle.Fill,
                Margin = new Padding(0)
            };
            row0.Controls.Add(floorSelPanel, 1, 0);

            var floorHeaderTop = new Label
            {
                Text = "(inside elevator)",
                Font = new Font("Courier New", 7),
                ForeColor = Color.FromArgb(130, 100, 20),
                BackColor = Color.FromArgb(10, 8, 2),
                Dock = DockStyle.Top,
                Height = 14,
                TextAlign = ContentAlignment.MiddleCenter
            };
            floorSelPanel.Controls.Add(floorHeaderTop);

            var floorHeaderMain = new Label
            {
                Text = "FLOOR SELECTION",
                Font = new Font("Courier New", 8, FontStyle.Bold),
                ForeColor = Color.FromArgb(220, 160, 20),
                BackColor = Color.FromArgb(22, 16, 2),
                Dock = DockStyle.Top,
                Height = 22,
                TextAlign = ContentAlignment.MiddleCenter
            };
            floorSelPanel.Controls.Add(floorHeaderMain);

            FloorButtonsPanel = new Panel
            {
                Dock = DockStyle.Fill,
                BackColor = Color.Transparent,
                Padding = new Padding(6)
            };
            floorSelPanel.Controls.Add(FloorButtonsPanel);

            FloorButtons = new Button[TotalFloors];
            for (int floor = TotalFloors; floor >= 1; floor--)
            {
                var btn = new Button
                {
                    Text = floor.ToString(),
                    Font = new Font("Courier New", 14, FontStyle.Bold),
                    BackColor = Color.FromArgb(52, 38, 10),    // dark amber off
                    ForeColor = Color.FromArgb(210, 160, 30),  // amber text
                    FlatStyle = FlatStyle.Flat,
                    Tag = floor,
                    Cursor = Cursors.Hand
                };
                btn.FlatAppearance.BorderColor = Color.FromArgb(130, 95, 15);
                btn.FlatAppearance.BorderSize = 2;
                FloorButtonsPanel.Controls.Add(btn);
                FloorButtons[floor - 1] = btn;
            }
            FloorButtonsPanel.Resize += (_, _) => LayoutFloorButtons();

            // ── Row 1: Elevator controls ──────────────────────────────────
            var ctrlOuter = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 1,
                RowCount = 2,
                BackColor = Color.FromArgb(28, 26, 18),     // dark amber-tinted panel
                Margin = new Padding(0, 0, 0, 4),
                CellBorderStyle = TableLayoutPanelCellBorderStyle.None
            };
            ctrlOuter.RowStyles.Add(new RowStyle(SizeType.Absolute, 28f));
            ctrlOuter.RowStyles.Add(new RowStyle(SizeType.Percent, 100f));
            ctrlOuter.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100f));
            rightOuter.Controls.Add(ctrlOuter, 0, 1);

            ctrlOuter.Controls.Add(new Label
            {
                Text = "ELEVATOR  CONTROLS",
                Font = new Font("Courier New", 10, FontStyle.Bold),
                ForeColor = Color.FromArgb(200, 150, 20),
                BackColor = Color.FromArgb(22, 18, 6),
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter
            }, 0, 0);

            var ctrlGrid = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 2,
                RowCount = 2,
                BackColor = Color.Transparent,
                Padding = new Padding(6, 4, 6, 4)
            };
            ctrlGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50f));
            ctrlGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 50f));
            ctrlGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 50f));
            ctrlGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 50f));
            ctrlOuter.Controls.Add(ctrlGrid, 0, 1);

            OpenDoorButton = MakeCtrlBtn("◀▶   OPEN DOOR", Color.FromArgb(160, 90, 0));    // deep orange-amber
            CloseDoorButton = MakeCtrlBtn("▶◀   CLOSE DOOR", Color.FromArgb(30, 36, 52));    // dark steel
            UpButton = MakeCtrlBtn("↑   UP", Color.FromArgb(30, 36, 52));
            DownButton = MakeCtrlBtn("↓   DOWN", Color.FromArgb(30, 36, 52));

            ctrlGrid.Controls.Add(OpenDoorButton, 0, 0);
            ctrlGrid.Controls.Add(CloseDoorButton, 1, 0);
            ctrlGrid.Controls.Add(UpButton, 0, 1);
            ctrlGrid.Controls.Add(DownButton, 1, 1);

            // ── Row 2: System controls ────────────────────────────────────
            var sysOuter = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 1,
                RowCount = 2,
                BackColor = Color.FromArgb(28, 26, 18),
                Margin = new Padding(0),
                CellBorderStyle = TableLayoutPanelCellBorderStyle.None
            };
            sysOuter.RowStyles.Add(new RowStyle(SizeType.Absolute, 28f));
            sysOuter.RowStyles.Add(new RowStyle(SizeType.Percent, 100f));
            sysOuter.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100f));
            rightOuter.Controls.Add(sysOuter, 0, 2);

            sysOuter.Controls.Add(new Label
            {
                Text = "SYSTEM  CONTROLS",
                Font = new Font("Courier New", 10, FontStyle.Bold),
                ForeColor = Color.FromArgb(200, 150, 20),
                BackColor = Color.FromArgb(22, 18, 6),
                Dock = DockStyle.Fill,
                TextAlign = ContentAlignment.MiddleCenter
            }, 0, 0);

            var sysGrid = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                ColumnCount = 3,
                RowCount = 1,
                BackColor = Color.Transparent,
                Padding = new Padding(6, 4, 6, 4)
            };
            sysGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.3f));
            sysGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.3f));
            sysGrid.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 33.3f));
            sysGrid.RowStyles.Add(new RowStyle(SizeType.Percent, 100f));
            sysOuter.Controls.Add(sysGrid, 0, 1);

            StartButton = MakeSysBtn("▶  START", Color.FromArgb(15, 90, 52));    // dark emerald
            PauseButton = MakeSysBtn("⏸  PAUSE", Color.FromArgb(145, 88, 0));    // dark amber
            StopButton = MakeSysBtn("⏹  STOP", Color.FromArgb(148, 22, 22));   // dark crimson

            sysGrid.Controls.Add(StartButton, 0, 0);
            sysGrid.Controls.Add(PauseButton, 1, 0);
            sysGrid.Controls.Add(StopButton, 2, 0);
        }

        // ── Layout helpers ────────────────────────────────────────────────
        internal void LayoutFloorButtons()
        {
            if (FloorButtons == null || FloorButtonsPanel == null) return;

            int pad = 6, gap = 5;
            int pw = FloorButtonsPanel.ClientSize.Width;
            int ph = FloorButtonsPanel.ClientSize.Height;
            if (pw <= 0 || ph <= 0) return;

            int cols = 2, rows = 2;
            int btnW = Math.Max(28, (pw - pad * 2 - gap * (cols - 1)) / cols);
            int btnH = Math.Max(28, (ph - pad * 2 - gap * (rows - 1)) / rows);

            // Square buttons — use smaller dimension
            int side = Math.Min(btnW, btnH);

            int gridW = cols * side + gap * (cols - 1);
            int gridH = rows * side + gap * (rows - 1);
            int startX = (pw - gridW) / 2;
            int startY = (ph - gridH) / 2;

            // Layout: row 0 = floors 4,3; row 1 = floors 2,1
            int[] floorOrder = { 4, 3, 2, 1 };
            for (int i = 0; i < floorOrder.Length; i++)
            {
                int floor = floorOrder[i];
                int col = i % cols;
                int row = i / cols;
                int bx = startX + col * (side + gap);
                int by = startY + row * (side + gap);
                var btn = FloorButtons[floor - 1];
                btn.SetBounds(bx, by, side, side);
                btn.Region = null;   // ensure square — no clipping region
            }
        }

        private static Button MakeCtrlBtn(string text, Color back)
        {
            var b = new Button
            {
                Text = text,
                Font = new Font("Courier New", 9, FontStyle.Bold),
                BackColor = back,
                ForeColor = Color.FromArgb(220, 200, 140),   // warm cream text
                FlatStyle = FlatStyle.Flat,
                Dock = DockStyle.Fill,
                Cursor = Cursors.Hand,
                Margin = new Padding(3),
                TextAlign = ContentAlignment.MiddleCenter
            };
            b.FlatAppearance.BorderColor = Color.FromArgb(120, 90, 20);
            b.FlatAppearance.BorderSize = 1;
            return b;
        }

        private static Button MakeSysBtn(string text, Color back)
        {
            var b = new Button
            {
                Text = text,
                Font = new Font("Courier New", 10, FontStyle.Bold),
                BackColor = back,
                ForeColor = Color.FromArgb(220, 200, 140),   // warm cream text
                FlatStyle = FlatStyle.Flat,
                Dock = DockStyle.Fill,
                Cursor = Cursors.Hand,
                Margin = new Padding(4),
                TextAlign = ContentAlignment.MiddleCenter
            };
            b.FlatAppearance.BorderColor = Color.FromArgb(120, 90, 20);
            b.FlatAppearance.BorderSize = 1;
            return b;
        }

        // ── Fields ────────────────────────────────────────────────────────
        private Label? CurrentFloorDisplay;
        private Panel? LcdContentPanel;
        private Button[]? FloorButtons;
        private Panel? FloorButtonsPanel;
        private Panel? ShaftPanel;
        private Label? StatusDirectionLabel;
        private Label? StatusDoorLabel;
        private Button? OpenDoorButton;
        private Button? CloseDoorButton;
        private Button? UpButton;
        private Button? DownButton;
        private Button? StartButton;
        private Button? PauseButton;
        private Button? StopButton;

        public Label? GetCurrentFloorDisplay() => CurrentFloorDisplay;
        public Panel? GetLcdContentPanel() => LcdContentPanel;
        public Button[]? GetFloorButtons() => FloorButtons;
        public Panel? GetFloorButtonsPanel() => FloorButtonsPanel;
        public Panel? GetShaftPanel() => ShaftPanel;
        public Label? GetStatusDirectionLabel() => StatusDirectionLabel;
        public Label? GetStatusDoorLabel() => StatusDoorLabel;
        public Button? GetOpenDoorButton() => OpenDoorButton;
        public Button? GetCloseDoorButton() => CloseDoorButton;
        public Button? GetUpButton() => UpButton;
        public Button? GetDownButton() => DownButton;
        public Button? GetStartButton() => StartButton;
        public Button? GetPauseButton() => PauseButton;
        public Button? GetStopButton() => StopButton;

        private void ShaftPanel_Paint(object? sender, PaintEventArgs e) { }
    }
}