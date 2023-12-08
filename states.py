from FeatureCloud.app.engine.app import AppState, app_state, Role
import time
import pandas as pd
import os

# FeatureCloud requires that apps define the at least the 'initial' state.
# This state is executed after the app instance is started.
@app_state('initial')
class InitialState(AppState):

    def register(self):
        self.register_transition('calculation')  
        # We declare that 'terminal' state is accessible from the 'initial' state.

    def run(self):
        # Checkout our documentation for help on how to implement an app
        # https://featurecloud.ai/assets/developer_documentation/getting_started.html
        dataFile = os.path.join(os.getcwd(), "mnt", "input", "data.csv")
        data = pd.read_csv(dataFile)
        self.store(key="data", value=data)
        
        return 'calculation'  
        # This means we are done. If the coordinator transitions into the 
        # 'terminal' state, the whole computation will be shut down.


@app_state('calculation')
class CalculationState(AppState):

    def register(self):
        self.register_transition('terminal')
        self.register_transition('aggregate', role=Role.COORDINATOR)  
        # We declare that 'terminal' state is accessible from the 'initial' state.

    def run(self):
        # Checkout our documentation for help on how to implement an app
        # https://featurecloud.ai/assets/developer_documentation/getting_started.html
        data = self.load("data")
        mean = data["salary"].sum()
        n = len(data["salary"])
        self.send_data_to_coordinator((mean, n), 
                                      send_to_self=True, 
                                      use_smpc=False, 
                                      use_dp=False)
        if self.is_coordinator:
            return "aggregate"
        else:
            return "terminal"
        

@app_state('aggregate')
class AggregateState(AppState):

    def register(self):
        self.register_transition('terminal')
        # We declare that 'terminal' state is accessible from the 'initial' state.

    def run(self):
        # Checkout our documentation for help on how to implement an app
        # https://featurecloud.ai/assets/developer_documentation/getting_started.html
        aggData = self.gather_data(use_smpc=False, use_dp=False)
        total_agg = 0
        total_n = 0
        for client_data in aggData:
            agg = client_data[0]
            n = client_data[1]
            total_agg += agg
            total_n += n
        resFile = os.path.join(os.getcwd(), "mnt", "output", "result.txt")
        with open(resFile, "w") as f:
            f.write(str(total_agg/total_n) + "\n")
        return "terminal"