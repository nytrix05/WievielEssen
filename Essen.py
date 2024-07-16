import openfoodfacts
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage

api = openfoodfacts.API(user_agent="Was darf rein ?")

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        layout = FloatLayout()
        
        label = Label(
            text="[b][u]Was darf rein?[/u][/b]", 
            font_size='30sp', 
            size_hint=(None, None),
            size=(900, 100),
            pos_hint={"center_x": 0.5, "center_y": 0.9},
            markup=True
        )
        layout.add_widget(label)
        
        label_desc = Label(text="Erfahre die Nährwerte deiner Produkte", size_hint=(0.5, 0.1), pos_hint={"x": 0.25, "y": 0.75})
        layout.add_widget(label_desc)
        
        self.input = TextInput(size_hint=(0.8, 0.1), pos_hint={"x": 0.1, "y": 0.6})
        layout.add_widget(self.input)
        
        button = ToggleButton(text="Suche", size_hint=(0.3, 0.1), pos_hint={"x": 0.35, "y": 0.4})
        button.bind(on_press=self.change_screen)
        layout.add_widget(button)
        
        self.add_widget(layout)
    
    def change_screen(self, instance):
        product_name = self.input.text
        self.manager.get_screen('second').update_result(product_name)
        self.manager.current = 'second'

class SecondScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        
        self.product_image = AsyncImage(size_hint=(None, None), size=(275, 250), pos_hint={"center_x": 0.5, "center_y": 0.65})
        self.layout.add_widget(self.product_image)

        self.result_label = Label(size_hint=(None, None), size=(900, 400), pos_hint={"center_x": 0.5, "center_y": 0.325})
        self.layout.add_widget(self.result_label)
        
        self.nutri_image = AsyncImage(size_hint=(None, None), size=(180, 75), pos_hint={"center_x":0.5, "center_y":0.185})
        self.layout.add_widget(self.nutri_image)
        
        self.barcode = AsyncImage(size_hint=(None, None), size=(300, 75), pos_hint={"center_x":0.5, "center_y":0.069})
        self.layout.add_widget(self.barcode)
        
        self.button = Button(
            background_normal="pfeil2.png",
            background_down="pfeil2.png",
            size=(75, 50),
            size_hint=(None, None),
            pos_hint={"center_y": 0.9, "center_x": 0.1}
        )
        self.button.bind(on_press=self.back)
        self.layout.add_widget(self.button)
        
        label = Label(
            text="[b][u]Was darf rein?[/u][/b]", 
            font_size='30sp', 
            size_hint=(None, None),
            size=(900, 100),
            pos_hint={"center_x": 0.5, "center_y": 0.9},
            markup=True
        )
        self.layout.add_widget(label)
        
        self.add_widget(self.layout)
    
    def back(self, instance):
        self.manager.current = "start"
        
    def update_result(self, product_name):
        products = api.product.text_search(product_name)
        if products["count"] > 0:
            product = products["products"][0]
            nutriments = product.get("nutriments", {})
            nutriscore_grade = product.get("nutriscore_grade", "N/A")
            barcode = product.get("code", "N/A")
            product_image_url = product.get("image_url", "")
            
            # Nutri-Score Bild URL
            if nutriscore_grade != "N/A":
                nutriscore_image_url = f"https://static.openfoodfacts.org/images/misc/nutriscore-{nutriscore_grade}.png"
            else:
                nutriscore_image_url = ""
            
            # Barcode Bild URL
            barcode_image_url = f"https://barcode.tec-it.com/barcode.ashx?data={barcode}&code=EAN13"
            
            # Set image sources
            self.product_image.source = product_image_url
            self.nutri_image.source = nutriscore_image_url
            self.barcode.source = barcode_image_url
            
            result = f"Produkt: {product.get('product_name', 'N/A')} auf 100g\n"
            result += f"Marke: {product.get('brands', 'N/A')}\n"
            result += f"Energie: {nutriments.get('energy-kcal_100g', 'N/A')} kcal\n"
            result += f"Kalorien: {nutriments.get('energy_100g', 'N/A')} kJ\n"
            result += f"Zucker: {nutriments.get('sugars_100g', 'N/A')} g\n"
            result += f"Eiweiße: {nutriments.get('proteins_100g', 'N/A')} g\n"
            
        else:
            result = "Kein Produkt gefunden"
            self.product_image.source = ""
            self.nutri_image.source = ""
            self.barcode.source = ""
            
        self.result_label.text = result
        
        
class WasDarfReinApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(SecondScreen(name='second'))
        return sm

if __name__ == "__main__":
    WasDarfReinApp().run()
