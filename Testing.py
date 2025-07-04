import locale
import matplotlib.pyplot as plt

# Set locale to use comma as decimal separator (e.g., Brazilian locale)
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Enable locale formatting for Matplotlib
plt.rcParams['axes.formatter.use_locale'] = True

# Plotting example
x = [1, 2, 3]
y = [1.23, 4.56, 7.89]
plt.plot(x, y)
plt.show()
