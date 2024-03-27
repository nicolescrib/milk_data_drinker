# Takes a question as an argument, prints the question, then asks for a Y/N response.
# Returns true for y/Y, false for anything else.
def yesno(response):
    if response.lower() == "y":
        return True
    else: 
        return False

# CLASS: MACRONUTRIENT
# A macronutrient is a single quality tested within a replicate. A replicate tests
# for many macronutrients. Macronutrients have a name and a value. They usually represent
# the fat, protein, calories, bioavailable protein, lactose, and solids in a sample
# of milk.
class Macronutrient:
    def __init__(self, name, value):
        self.name = name
        self.value = value

# CLASS: REPLICATE
# A replicate is a single test (of many) performed on a sample.
# Replicates might be individual tests, or they might represent the mean
# or standard deviation of a group of tests. 
# Replicates are either numbered or are named according to the values they represent.
# Flags indicate that this replicate represents a special value.
class Replicate:
    def __init__(self, name, macronutrients):
        self.name = name
        self.macronutrients = macronutrients
        self.mean_flag = False
        self.stddev_flag = False
        self.reference_flag = False
        self.difference_flag = False
        if not name.isnumeric():
            self.set_flags()

    # Returns string with name of replicate and number of macronutrients tested
    def __str__(self):
        return f"Replicate {self.name}: {len(self.macronutrients)} macronutrients."

    # Append one macronutrient to replicate
    def add_macronutrient(self, macronutrient):
        if macronutrient is None:
            print(f"Replicate {self.name}: No macronutrient to add")
        self.macronutrients.append(macronutrient)

    # Sets flags to identify replicate as representing the mean, standard deviation,
    # reference (for pilot), or difference (for pilot)
    def set_flags(self):
        if self.name is "mean" or self.name is "Mean":
            self.mean_flag = True
        else:
            self.mean_flag = False
        
        if self.name.lower() is "stddev":
            self.stddev_flag = True
        else:
            self.stddev_flag = False

        if self.name.lower() is "reference":
            self.reference_flag = True
        else:
            self.reference_flag = False

        if self.name.lower() is "difference":
            self.difference_flag = True
        else:
            self.difference_flag = False

# CLASS: SAMPLE
# A donor, test, cleaning, or other instance of an analyzer run.
# Samples have several replicates (tests)
# Samples have a mean replicate and a standard deviation replicate.
class Sample:
    def __init__(self, name, type, date, replicates):
        self.name = name
        self.type = type
        self.date = date
        self.replicates = replicates 
        self.mean_replicate = None
        self.stddev_replicate = None
        self.reference_replicate = None
        self.difference_replicate = None
        self.set_special_replicates()

    # Returns string with name, date, and number of associated replicates
    def __str__(self):
        return f"{self.name} {self.date}: {len(self.replicates)} replicates."

    # Adds a new replicate and updates special replicate accordingly
    def add_replicate(self, replicate):
        if replicate is None:
            print(f"{self.name}: No replicate to add.")
            return
        self.replicates.append(replicate)

        # Update special replicate if appropriate
        if replicate.name.lower() == "mean":
            self.set_mean_replicate(replicate)
            return
        if replicate.name.lower() == "stddev":
            self.set_stddev_replicate(replicate)
            return
        if replicate.name.lower() == "difference":
            self.set_difference_replicate(replicate)
            return
        if replicate.name.lower() == "reference":
            self.set_reference_replicate(replicate)
            return

    # If a special replicate hasn't been set, search for one and update it.
    def set_special_replicates(self):
        if self.mean_replicate == None:
            self.set_mean_replicate(self.find_mean_replicate())
        if self.stddev_replicate == None:
            self.set_stddev_replicate(self.find_stddev_replicate())
        if self.reference_replicate == None:
            self.set_reference_replicate(self.find_reference_replicate())
        if self.difference_replicate == None:
            self.set_difference_replicate(self.find_difference_replicate())

    # Find special replicates or return None
    def find_mean_replicate(self):
        for replicate in self.replicates:
            if replicate.name.lower() == "mean":
                return replicate
        return None

    def find_stddev_replicate(self):
        for replicate in self.replicates:
            if replicate.name.lower() == "stddev":
                return replicate
        return None
            
    def find_difference_replicate(self):
        for replicate in self.replicates:
            if replicate.name.lower() == "difference":
                return replicate
        return None

    def find_reference_replicate(self):
        for replicate in self.replicates:
            if replicate.name.lower() == "reference":
                return replicate
        return None

    # Set special replicates
    def set_mean_replicate(self, replicate):
        self.mean_replicate = replicate

    def set_stddev_replicate(self, replicate):
        self.stddev_replicate = replicate

    def set_reference_replicate(self, replicate):
        self.reference_replicate = replicate

    def set_difference_replicate(self, replicate):
        self.difference_replicate = replicate