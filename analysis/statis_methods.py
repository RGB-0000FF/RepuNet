from analysis import *
import matplotlib.pyplot as plt 
import seaborn as sns
import statsmodels.api as sm
import pandas as pd
import json
from scipy.stats import sem, t
import numpy as np
class Linear_Regression:
    def __init__(self, x, y, xlabel, ylabel,title) -> None:
        data = {xlabel: x, ylabel: y}
        self.data = pd.DataFrame(data)
        self.model = None
        self.result = None
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title=title
    def OLS(self):
        X = self.data[self.xlabel]
        Y = self.data[self.ylabel]
        X = sm.add_constant(X)
        self.model = sm.OLS(Y, X).fit()
        self.result = self.model.summary()

    def return_result(self):
        return self.result
    
    def Logistic(self):
        X = self.data[self.xlabel]
        Y = self.data[self.ylabel]
        X = sm.add_constant(X)
        self.model = sm.Logit(Y, X).fit()
        self.result = self.model.summary()
        
    def visualization(self,color_list=[]):
        if color_list:
            data=dict(self.data)
            data1={}
            data2={}
            x1=[]
            x2=[]
            y1=[]
            y2=[]
            for i in range(len(color_list)):
                if color_list[i]=="red":
                    x1.append(data[self.xlabel][i])
                    y1.append(data[self.ylabel][i])
                elif color_list[i]=="blue":
                    x2.append(data[self.xlabel][i])
                    y2.append(data[self.ylabel][i])
            data1[self.xlabel]=x1
            data1[self.ylabel]=y1
            data2[self.xlabel]=x2
            data2[self.ylabel]=y2
            
            
        plt.figure(figsize=(10, 6))
        if color_list:
            sns.scatterplot(x=self.xlabel, y=self.ylabel, data=data1, color="red", label="Sign up in the final round")
            sns.scatterplot(x=self.xlabel, y=self.ylabel, data=data2, color="blue", label="Not sign up in the final round")
        else:
            sns.scatterplot(x=self.xlabel, y=self.ylabel, data=self.data, color='blue', label="Original data")
        x1_vals = self.data[self.xlabel]
        predicted_y = self.model.predict(sm.add_constant(x1_vals))
        plt.plot(x1_vals, predicted_y, color='orange', label='Fitted Line', linewidth=2)
        # plt.title('Trial 1: Linear regression of the Number of Double Positive Connect and reputation')
        plt.title(self.title)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.legend()
        plt.show()

def Gini_coef(analysis_dict):
    resource_list = [i["resources_unit"] for i in analysis_dict.values()]       
    if not resource_list:
        return 0

    sorted_values = sorted(resource_list)
    n = len(resource_list)
    cumulative_values = [sum(sorted_values[:i+1]) for i in range(n)]
    total = cumulative_values[-1]

    gini_sum = sum((i + 1) * value for i, value in enumerate(sorted_values))
    gini_index = (2 * gini_sum) / (n * total) - (n + 1) / n

    return gini_index


def persona_invest_willingness(analysis_dict):
    invest_list={}
    for i,j in list(analysis_dict.items()):
        if i==j["investor"]:
            if j["investment_status"]=="success":
                invest_list[i]=float(j["investor_invests_unit"])/float(j["resources_unit"])
            elif j["investment_status"]=="failed":
                invest_list[i]=0
    return invest_list

def invest_willingness(analysis_dict):
    total_investment=0
    total_investor_units=0
    for i,j in list(analysis_dict.items()):
        if i==j["investor"]:
            if j["investment_status"]=="success":
                total_investment+=float(j["investor_invests_unit"])
                total_investor_units+=float(j["resources_unit"])
            elif j["investment_status"]=="failed":
                total_investment+=0
                total_investor_units+=float(j["resources_unit"])
    return total_investment/total_investor_units  
    
def persona_income(analysis_dict):
    result={}
    for i,j in list(analysis_dict.items()):
        result[i]=j["resources_unit"]
    return result

def cheat_coef(analysis_dict):
    cheat_list={}
    for i,j in list(analysis_dict.items()):
        if j["investment_status"]=="failed":
            if i==j["trustee"]:
                cheat_list[i]=0
        elif j["investment_status"]=="success":
            if i==j["trustee"]:
                try:
                    p=float(j["trustee_plan"].split("retains")[-1].split("%")[0].strip())/100
                    cheat_list[i]=max(0,1-(float(j["trustee_allocation"]["investor"])/((1+p)*float(j["investor_invests_unit"]))))
                except:
                    cheat_list[i]=0
    return cheat_list

def plot(x,y,title,xlabel,ylabel):
    plt.plot(x,y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(0,len(x))
    plt.show()
    
def plot_distribution(data_list, title,xlabel,ylabel):
    
    data = []
    for year, wealth_dict in enumerate(data_list):
        for person, wealth in wealth_dict.items():
            data.append({'year': year, 'person': person, 'wealth': wealth})
    
    df = pd.DataFrame(data)
    # 平均值和95%置信区间
    stats = df.groupby('year')['wealth'].agg(['mean', 'count', 'std']).reset_index()
    confidence = 0.95
    h = stats['std'] * t.ppf((1 + confidence) / 2, stats['count'] - 1) / np.sqrt(stats['count'])

    
    plt.figure(figsize=(14, 7))

    
    plt.plot(stats['year'], stats['mean'], label=ylabel, color='blue')

    
    plt.fill_between(stats['year'], stats['mean'] - h, stats['mean'] + h, color='lightblue', alpha=0.5, label='95% Confidence Interval')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    sims = get_all_sim_info("investment_s1")
    y=[cheat_coef(sim.analysis_dict) for sim in sims]
    plot_distribution(y,"Cheat Coefficient","Round","Mean cheat Coefficient")
    # x=list(range(1,len(y)+1))
    # l=Linear_Regression(x,y,"Round","Gini Coefficient","Gini Coefficient of each round")
    # l.OLS()
    # l.visualization()
    # print(l.return_result())
    # plot_wealth_distribution(y,"Wealth Distribution","Round","Wealth")