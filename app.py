import flet as ft
from flet import (
    Page,
    View,
    Container,
    Column,
    Row,
    Text,
    Icon,
    IconButton,
    PopupMenuButton,
    PopupMenuItem,
    GestureDetector,
    Stack,
    Image,
    GridView,
    FilePicker,
    FilePickerResultEvent,
    TextField,
    Dropdown,
    ElevatedButton,
    SnackBar,
    TextAlign,
    ImageFit,
    ButtonStyle,
    TextOverflow,
    CrossAxisAlignment,
    MainAxisAlignment,
    Animation,
    AnimationCurve,
    padding,
    dropdown,
    FilePickerFileType,
    Colors,
    Icons,
)
import os
import json
import subprocess
import shutil
from PIL import Image

class FavoriteAppsManager:
    def __init__(self):
        self.apps_data = {}
        self.categories = {'Uncategorized'}
        self.icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
        os.makedirs(self.icons_dir, exist_ok=True)
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists('favorite_apps.json'):
                with open('favorite_apps.json', 'r') as f:
                    data = json.load(f)
                    self.apps_data = data.get('apps', {})
                    self.categories = set(data.get('categories', ['Uncategorized']))
        except:
            self.apps_data = {}
            self.categories = {'Uncategorized'}

    def save_data(self):
        with open('favorite_apps.json', 'w') as f:
            json.dump({
                'apps': self.apps_data,
                'categories': list(self.categories)
            }, f)

    def process_icon(self, icon_path):
        try:
            filename = os.path.basename(icon_path)
            dest_path = os.path.join(self.icons_dir, filename)
            
            # Copy and process icon
            with Image.open(icon_path) as img:
                img = img.convert('RGBA')
                img.thumbnail((48, 48), Image.Resampling.LANCZOS)
                img.save(dest_path, 'PNG')
            
            return dest_path
        except Exception as e:
            print(f"Error processing icon: {str(e)}")
            return None

def main(page: ft.Page):
    page.title = "Favorite Applications Manager"
    page.window_width = 1000
    page.window_height = 600
    page.padding = 0
    
    # Initialize app manager
    app_manager = FavoriteAppsManager()
    
    # Create views
    main_view = ft.View("/", horizontal_alignment="center")
    add_view = ft.View("/add", horizontal_alignment="center")
    
    def remove_app(app_name):
        if app_name in app_manager.apps_data:
            # Remove icon if exists
            if app_manager.apps_data[app_name].get("icon"):
                try:
                    os.remove(app_manager.apps_data[app_name]["icon"])
                except:
                    pass
            
            # Remove app from data
            del app_manager.apps_data[app_name]
            
            # Update categories
            used_categories = {'Kategorisiz'}
            for app_data in app_manager.apps_data.values():
                used_categories.add(app_data.get('category', 'Kategorisiz'))
            app_manager.categories = used_categories
            
            # Save and update view
            app_manager.save_data()
            update_main_view()
            
            # Show confirmation message
            page.snack_bar = ft.SnackBar(content=ft.Text(f"{app_name} başarıyla kaldırıldı"))
            page.snack_bar.open = True
            page.update()
    
    def create_app_tile(app_name, app_data):
        def show_context_menu(e):
            # Create menu items
            menu = ft.Container(
                content=ft.Column(
                    [
                        ft.TextButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.DELETE_OUTLINED, color=ft.Colors.RED),
                                    ft.Text("Kaldır", color=ft.Colors.RED),
                                ],
                                spacing=10,
                            ),
                            on_click=lambda _: remove_app(app_name),
                        ),
                    ],
                ),
                bgcolor=ft.Colors.SURFACE,
                border_radius=10,
                padding=5,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color=ft.Colors.BLACK,
                    offset=ft.Offset(0, 0),
                ),
            )
            
            # Show menu at click position
            e.control.content.content.controls.append(menu)
            page.update()
            
            # Remove menu when clicked outside
            def remove_menu(_):
                if menu in e.control.content.content.controls:
                    e.control.content.content.controls.remove(menu)
                    page.update()
            
            page.on_click = remove_menu

        return ft.GestureDetector(
            on_double_tap=lambda e: launch_app(app_data["path"]),
            on_secondary_tap=show_context_menu,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Stack(
                            [
                                ft.Image(
                                    src=app_data.get("icon", ""),
                                    width=48,
                                    height=48,
                                    fit=ft.ImageFit.CONTAIN,
                                    visible=bool(app_data.get("icon")),
                                ) if app_data.get("icon") else ft.Icon(
                                    ft.Icons.APPS_OUTLINED,
                                    size=48,
                                    color=ft.Colors.BLUE_GREY_400,
                                ),
                            ],
                            width=48,
                            height=48,
                        ),
                        ft.Text(
                            app_name,
                            size=12,
                            text_align=ft.TextAlign.CENTER,
                            width=100,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Container(
                            content=ft.Text(
                                app_data.get("category", "Kategorisiz"),
                                size=10,
                                color=ft.Colors.BLUE_GREY_400,
                            ),
                            visible=app_data.get("category") != "Kategorisiz",
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                ),
                width=120,
                height=120,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE,
                opacity=0.8,
                padding=10,
                animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
                on_hover=lambda e: setattr(e.control, 'opacity', 0.9 if e.data == "true" else 0.8),
            )
        )

    def show_context_menu(e, app_name):
        menu = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    text="Kaldır",
                    icon=ft.Icons.DELETE_OUTLINED,
                    on_click=lambda _: remove_app(app_name)
                ),
            ],
        )
        # Trigger the menu programmatically at the mouse position
        e.control.content.content = menu
        menu.show_menu(e)
        page.update()

    def update_main_view():
        # Clear existing content
        main_view.controls.clear()
        
        # Top navigation bar
        top_bar = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.APPS_OUTLINED),
                    ft.Text("Favorite Applications", size=20, weight=ft.FontWeight.BOLD),
                    ft.PopupMenuButton(
                        items=[
                            ft.PopupMenuItem(
                                text=category,
                                on_click=lambda e, cat=category: filter_apps(cat)
                            ) for category in ["Tüm Kategoriler"] + sorted(list(app_manager.categories))
                        ],
                        icon=ft.Icons.FILTER_LIST_OUTLINED,
                        tooltip="Kategoriye Göre Filtrele",
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD_OUTLINED,
                        on_click=lambda _: page.go("/add"),
                        tooltip="Uygulama Ekle",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            bgcolor=ft.Colors.SURFACE,
            opacity=0.9,
        )
        
        # Apps grid
        apps_grid = ft.GridView(
            expand=True,
            max_extent=150,
            spacing=20,
            run_spacing=20,
            padding=20,
            child_aspect_ratio=1,
        )
        
        # Filter apps if needed
        selected_category = getattr(page, 'selected_category', 'All Categories')
        for app_name, app_data in app_manager.apps_data.items():
            if (selected_category == 'All Categories' or 
                app_data.get('category', 'Uncategorized') == selected_category):
                apps_grid.controls.append(create_app_tile(app_name, app_data))
        
        if not apps_grid.controls:
            apps_grid.controls.append(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.FOLDER_OUTLINED, size=64, color=ft.Colors.BLUE_GREY_400),
                        ft.Text("Uygulama bulunamadı", size=16, color=ft.Colors.BLUE_GREY_400),
                        ft.Text("Uygulama eklemek için + simgesine tıklayın", size=14, color=ft.Colors.BLUE_GREY_400),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                )
            )
        
        main_view.controls.extend([top_bar, apps_grid])
        page.update()

    def create_add_view():
        add_view.controls.clear()
        
        def pick_files_result(e: ft.FilePickerResultEvent):
            if e.files:
                app_path_field.value = e.files[0].path
                page.update()

        def pick_icon_result(e: ft.FilePickerResultEvent):
            if e.files:
                icon_path_field.value = e.files[0].path
                page.update()

        file_picker = ft.FilePicker(on_result=pick_files_result)
        icon_picker = ft.FilePicker(on_result=pick_icon_result)
        page.overlay.extend([file_picker, icon_picker])

        app_path_field = ft.TextField(
            label="Uygulama Yolu",
            width=400,
            helper_text="Çalıştırılabilir dosyayı seçin (.exe)",
        )

        icon_path_field = ft.TextField(
            label="Özel Simge (İsteğe Bağlı)",
            width=400,
            helper_text="Simge için bir resim dosyası seçin",
        )

        category_dropdown = ft.Dropdown(
            label="Kategori",
            width=400,
            options=[
                ft.dropdown.Option(category)
                for category in sorted(list(app_manager.categories))
            ],
            value="Kategorisiz",
        )

        new_category_field = ft.TextField(
            label="Yeni Kategori",
            width=300,
            visible=False,
        )

        def toggle_new_category(e):
            new_category_field.visible = not new_category_field.visible
            page.update()

        def add_application(e):
            app_path = app_path_field.value
            if not app_path or not os.path.exists(app_path):
                page.snack_bar = ft.SnackBar(content=ft.Text("Lütfen geçerli bir uygulama seçin"))
                page.snack_bar.open = True
                page.update()
                return

            app_name = os.path.basename(app_path)
            category = new_category_field.value if new_category_field.visible else category_dropdown.value
            
            # Process icon if provided
            icon_path = icon_path_field.value
            if icon_path and os.path.exists(icon_path):
                icon_dest = app_manager.process_icon(icon_path)
            else:
                icon_dest = None

            # Add application
            app_manager.apps_data[app_name] = {
                "path": app_path,
                "icon": icon_dest,
                "category": category
            }

            # Update categories
            if category not in app_manager.categories:
                app_manager.categories.add(category)

            # Save and update
            app_manager.save_data()
            page.go("/")

        add_view.controls.extend([
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_OUTLINED,
                            on_click=lambda _: page.go("/"),
                            tooltip="Geri",
                        ),
                        ft.Text("Uygulama Ekle", size=20, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
                bgcolor=ft.Colors.SURFACE,
                opacity=0.9,
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [app_path_field, ft.IconButton(icon=ft.Icons.FOLDER_OUTLINED, 
                                                         on_click=lambda _: file_picker.pick_files(
                                            allow_multiple=False,
                                            file_type=ft.FilePickerFileType.CUSTOM,
                                            allowed_extensions=['exe'],
                                        ),
                                        tooltip="Uygulama Seç")],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [icon_path_field, ft.IconButton(icon=ft.Icons.IMAGE_OUTLINED, 
                                                          on_click=lambda _: icon_picker.pick_files(
                                            allow_multiple=False,
                                            file_type=ft.FilePickerFileType.CUSTOM,
                                            allowed_extensions=['png', 'jpg', 'jpeg', 'ico'],
                                        ),
                                        tooltip="Simge Seç")],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            [
                                category_dropdown,
                                ft.IconButton(
                                    icon=ft.Icons.ADD_OUTLINED,
                                    on_click=toggle_new_category,
                                    tooltip="Yeni Kategori Ekle",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        new_category_field,
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "İptal",
                                    on_click=lambda _: page.go("/"),
                                ),
                                ft.ElevatedButton(
                                    "Uygulama Ekle",
                                    on_click=add_application,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                padding=ft.padding.all(20),
            ),
        ])
        page.update()

    def launch_app(app_path):
        try:
            subprocess.Popen([app_path])
        except Exception as e:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Error launching application: {str(e)}"))
            page.snack_bar.open = True
            page.update()

    def filter_apps(category):
        page.selected_category = category
        update_main_view()

    def route_change(e):
        page.views.clear()
        
        if page.route == "/add":
            create_add_view()
            page.views.append(add_view)
        else:
            update_main_view()
            page.views.append(main_view)
            
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

ft.app(target=main) 
