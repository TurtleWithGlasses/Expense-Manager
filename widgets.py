from PySide6.QtWidgets import QPushButton

class CategoryCard(QPushButton):
    def __init__(self, name: str, total: float, parent=None):
        super().__init__(parent)
        self.name = name
        self.total = total
        self.setText(f"{name}\n{total:.2f}")
        self.setFixedSize(150, 80)
        self.setCheckable(False)
        self.setStyleSheet(
            """
            QPushButton {
                border: 2px solid #333; border-radius: 12px; padding: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background: #f3f3f3; }
            """
        )

    def update_total(self, total: float):
        self.total = total
        self.setText(f"{self.name}\n{total:.2f}")


class StatBox(QPushButton):
    """Clickable box with title and big number."""
    def __init__(self, title: str, color: str = "#2f8a00", parent=None):
        super().__init__(parent)
        self.title = title
        self.amount = 0.0
        self.color = color
        self.setMinimumHeight(70)
        self.setStyleSheet(
            f"border:2px solid {color}; border-radius:14px; padding:10px; color:{color}; font-weight:700;"
        )
        self.setText(self._render())

    def _render(self) -> str:
        # Use HTML to separate title and number (prevents adjacency like 'Balance475...')
        return f"{self.title}\n{self.amount:,.2f}"

    def set_amount(self, amount: float):
        self.amount = float(amount or 0)
        self.setText(self._render())