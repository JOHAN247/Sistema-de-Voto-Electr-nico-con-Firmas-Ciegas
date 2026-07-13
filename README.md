# 🗳️ Sistema Universitario de Votación Anónima con Firmas Ciegas

Herramienta interactiva en **Python + Streamlit** para realizar elecciones y votaciones estudiantiles seguras, utilizando el protocolo criptográfico de **Firmas Ciegas de David Chaum**. 

La aplicación permite simular un entorno electoral real donde el voto es **100% anónimo**, pero matemáticamente verificable para evitar fraudes, dobles votaciones o suplantaciones.

---

## 🚀 Demo en línea

**App desplegada en Streamlit:**  
[🔗 Abrir Sistema de Votación](https://TU-APP.streamlit.app)

> *Nota: Si el enlace no funciona o carga lento, es posible que la aplicación esté inactiva ("dormida"). Solo espera unos segundos a que el contenedor de Streamlit Cloud se vuelva a iniciar.*

---

## 🖼️ Vista previa

*Pantalla de votación activa y resultados oficiales en tiempo real:*
![Screenshot de la app](img/screenshot.png)

---

## ✨ Características principales

- ✅ **Sin activación manual:** Los usuarios pueden votar inmediatamente ingresando el código de la sala sin que el administrador deba habilitar la urna.
- ✅ **Diseño estilo Kahoot:** Flujo simplificado mediante códigos únicos de 6 caracteres para unirse a las salas de votación.
- ✅ **Gestión de Roles:** Diferenciación en tiempo real entre el panel de control del Administrador (creador de la sala) y los Participantes (votantes).
- ✅ **Seguridad Criptográfica:** Implementación matemática real del protocolo RSA Blind Signature. El servidor firma el voto sin conocer la opción que el usuario eligió.
- ✅ **Escrutinio Transparente:** Reconteo automático de los votos válidos al cerrarse la urna, graficando los resultados finales en tiempo real.

---

## 🧠 Fundamento matemático

El proyecto se basa en las **Firmas Ciegas de David Chaum (1983)**, una aplicación avanzada de la teoría de números y la aritmética modular de **Matemáticas Discretas**:

1. **Cegado ($m_c$):** El votante toma su voto $m$ (convertido a entero), elige un factor de cegado aleatorio $r$ coprimo con $n$ (donde $n$ es el módulo público de la autoridad) y envía al servidor:
   $$m_c \equiv m \cdot r^e \pmod n$$

2. **Firma de la Autoridad ($s_c$):** El servidor firma el mensaje cegado sin poder ver su contenido real, utilizando su llave privada $d$:
   $$s_c \equiv (m_c)^d \pmod n$$

3. **Descegado ($s$):** El votante recibe la firma del servidor y remueve matemáticamente el factor de cegado para obtener la firma digital legítima del voto original:
   $$s \equiv s_c \cdot r^{-1} \pmod n \equiv m^d \pmod n$$

Al final, el votante envía de manera anónima su voto $m$ junto a la firma válida $s$ a una urna pública. Cualquier persona puede verificar la autenticidad del voto comprobando que:
$$s^e \equiv m \pmod n$$

---

## 🛠️ Tecnologías utilizadas

- 🐍 **Python 3**
- 🎈 **Streamlit** (Capa de Presentación)
- 🗄️ **SQLite3** (Persistencia y Sincronización)
- 🔑 **Bcrypt** (Seguridad de Credenciales)

---

## 💻 Cómo ejecutar el proyecto localmente

```bash
# 1. Clonar el repositorio
git clone [https://github.com/TU-USUARIO/sistema-de-voto-electronico-con-firmas-ciegas.git](https://github.com/TU-USUARIO/sistema-de-voto-electronico-con-firmas-ciegas.git)
cd sistema-de-voto-electronico-con-firmas-ciegas

# 2. (Opcional) Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la app localmente
streamlit run app.py
