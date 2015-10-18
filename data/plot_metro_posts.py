import pandas as pd
import matplotlib.pyplot as plt

filename = './data/us_metro_population.csv'
df = pd.read_csv(filename)

plt.scatter(df.population, df.n_images)
ax = plt.gca()
plt.title('Posts with #foodie tag on Instagram in US', fontsize=14, fontweight='bold')
plt.ylabel('Number of Posts', fontsize=12, fontweight='bold')
plt.xlabel('Population (metro area)', fontsize=12, fontweight='bold')
ax.set_yscale('log')
plt.ylim((1,10000))
ax.set_xscale('log')

#axs = plt.axes()
#axs.arrow(0, 0, 100000, 3000, head_width=0.05, head_length=0.1, fc='k', ec='k')
plt.grid(True,which="both")

plt.savefig('posts_pop.png', bbox_inches='tight', dpi = 300)
plt.show()



