import milk_analyzer
import pytest

def test_yesno():
    assert(milk_analyzer.yesno("y"))
    assert(milk_analyzer.yesno("Y"))
    assert(milk_analyzer.yesno("N") == False)
    assert(milk_analyzer.yesno("n") == False)
    assert(milk_analyzer.yesno("t") == False)

@pytest.fixture
def fat_setup():
    object = milk_analyzer.Macronutrient("Fat", 0.345)
    return object

@pytest.fixture
def protein_setup():
    object = milk_analyzer.Macronutrient("Protein", 1.289)
    return object

@pytest.fixture
def calorie_setup():
    object = milk_analyzer.Macronutrient("Calorie", 36)
    return object

@pytest.fixture
def replicate_setup(fat_setup, protein_setup, calorie_setup):
    macronutrients_array = [fat_setup, protein_setup, calorie_setup]
    object = milk_analyzer.Replicate("#01", macronutrients_array)
    return object

@pytest.fixture
def replicate_mean_setup(fat_setup, protein_setup, calorie_setup):
    macronutrients_array = [fat_setup, protein_setup, calorie_setup]
    object = milk_analyzer.Replicate("Mean", macronutrients_array)
    return object

@pytest.fixture
def sample_setup(replicate_setup, replicate_mean_setup):
    replicate_array = [replicate_setup, replicate_mean_setup]
    object = milk_analyzer.Sample("sample01", "Raw", "3/16/2024", replicate_array)
    return object

def test_macronutrient(fat_setup):
    assert(fat_setup.name == "Fat")
    assert(fat_setup.value == 0.345)

def test_replicate(replicate_setup, replicate_mean_setup):
    assert(replicate_setup.name == "#01")
    assert(len(replicate_setup.macronutrients) == 3)
    assert(replicate_setup.macronutrients[0].name == "Fat")
    assert(replicate_setup.mean_flag == False)
    assert(replicate_mean_setup.mean_flag == True)
    assert(replicate_setup.__str__() == "Replicate #01: 3 macronutrients.")

def test_sample(sample_setup):
    assert(sample_setup.name == "sample01")
    assert(sample_setup.type == "Raw")
    assert(sample_setup.date == "3/16/2024")
    assert(sample_setup.stddev_replicate == None)
    assert(sample_setup.mean_replicate)