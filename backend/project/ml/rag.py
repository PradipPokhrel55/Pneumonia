from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from threading import Lock

# Documents (kept at module-level as static data)
docs = [
 
    "Pneumonia is an infection that inflames the air sacs in one or both lungs.",
    "The alveoli may fill with fluid or pus, causing cough, fever, chills, and difficulty breathing.",
    "Pneumonia can range from mild to life-threatening depending on age, health condition, and infectious agent.",
    "Pneumonia affects millions of people worldwide every year and is a major cause of death in children and elderly adults.",
    "The infection may affect one lobe of the lung, multiple lobes, or both lungs entirely.",

    # Types of Pneumonia
    "Bacterial pneumonia is commonly caused by Streptococcus pneumoniae and Haemophilus influenzae.",
    "Viral pneumonia can be caused by influenza virus, RSV, or SARS-CoV-2.",
    "Fungal pneumonia occurs more often in people with weakened immune systems.",
    "Community-acquired pneumonia develops outside hospitals or healthcare facilities.",
    "Hospital-acquired pneumonia occurs 48 hours or more after hospital admission.",
    "Ventilator-associated pneumonia develops in patients using mechanical ventilators.",
    "Aspiration pneumonia occurs when food, liquid, saliva, or vomit enters the lungs.",
    "Walking pneumonia is a mild form of pneumonia commonly caused by Mycoplasma pneumoniae.",
    "Lobar pneumonia affects a large and continuous area of a lobe of the lung.",
    "Bronchopneumonia causes patchy inflammation around the bronchi in multiple areas of the lungs.",

    # Causes
    "Pneumonia can be caused by bacteria, viruses, fungi, or parasites.",
    "Streptococcus pneumoniae is the most common bacterial cause of pneumonia.",
    "Influenza viruses can weaken lung defenses and increase pneumonia risk.",
    "COVID-19 can lead to severe viral pneumonia and acute respiratory distress syndrome.",
    "Aspiration of gastric contents can introduce bacteria into the lungs.",
    "People with weakened immunity are more vulnerable to opportunistic fungal infections.",
    "Smoking damages the natural defense mechanisms of the respiratory tract.",
    "Air pollution and toxic fumes may increase susceptibility to respiratory infections.",

    # Symptoms
    "Symptoms of pneumonia include cough, fever, chills, chest pain, fatigue, and shortness of breath.",
    "Some patients produce thick yellow, green, or blood-tinged mucus.",
    "Rapid breathing and rapid heartbeat are common signs of severe pneumonia.",
    "Older adults may experience confusion or altered mental status instead of fever.",
    "Children with pneumonia may show poor feeding, irritability, and bluish skin coloration.",
    "Chest pain often worsens during coughing or deep breathing.",
    "Severe pneumonia can reduce oxygen levels in the blood.",
    "Persistent fatigue and weakness may continue even after infection improves.",

    # Risk Factors
    "Risk factors include age below 2 or above 65, chronic diseases, smoking, and weak immunity.",
    "Diabetes increases the risk of pneumonia and related complications.",
    "Chronic obstructive pulmonary disease and asthma increase vulnerability to lung infections.",
    "Cancer treatments such as chemotherapy can suppress the immune system.",
    "Alcohol abuse weakens immune defenses and increases aspiration risk.",
    "Malnutrition can reduce the body's ability to fight infection.",
    "Long hospital stays increase exposure to antibiotic-resistant bacteria.",
    "People living in crowded environments are at greater risk of respiratory infections.",

    # Diagnosis
    "Diagnosis involves chest X-ray, blood tests, sputum tests, and physical examination.",
    "Doctors may use pulse oximetry to measure oxygen saturation levels.",
    "CT scans can provide more detailed images of lung infection.",
    "Blood cultures may help identify bacteria causing severe pneumonia.",
    "Sputum culture tests identify pathogens present in mucus from the lungs.",
    "Arterial blood gas analysis measures oxygen and carbon dioxide levels in the blood.",
    "Bronchoscopy may be used in complicated or unclear cases.",
    "Physical examination may reveal crackling sounds in the lungs during breathing.",

    # Treatment
    "Treatment depends on the cause: antibiotics for bacterial, antivirals for viral, and antifungals for fungal pneumonia.",
    "Severe pneumonia may require hospitalization and oxygen therapy.",
    "Patients with respiratory failure may need mechanical ventilation.",
    "Rest and hydration help support recovery from pneumonia.",
    "Over-the-counter fever reducers may help control fever and discomfort.",
    "Antibiotic resistance can make bacterial pneumonia harder to treat.",
    "Early treatment usually improves outcomes and reduces complications.",
    "Patients should complete the full course of prescribed antibiotics.",

    # Prevention
    "Vaccination, good hygiene, and a healthy lifestyle help prevent pneumonia.",
    "Pneumococcal vaccines protect against common bacterial causes of pneumonia.",
    "Annual influenza vaccination lowers the risk of viral pneumonia.",
    "Frequent handwashing reduces the spread of respiratory pathogens.",
    "Avoiding smoking helps maintain healthy lung function.",
    "Proper nutrition and regular exercise support immune health.",
    "Wearing masks during outbreaks can reduce respiratory infection transmission.",
    "Breastfeeding helps strengthen immunity in infants.",

    # Complications
    "Complications of pneumonia include respiratory failure, sepsis, lung abscess, and pleural effusion.",
    "Untreated pneumonia can spread infection into the bloodstream.",
    "Pleural effusion occurs when fluid accumulates around the lungs.",
    "Sepsis is a life-threatening response to infection that may damage organs.",
    "Lung abscesses are pus-filled cavities that may form in infected lung tissue.",
    "Acute respiratory distress syndrome can develop in severe pneumonia cases.",
    "Repeated pneumonia infections may cause long-term lung damage.",
    "Severe complications are more common in elderly and immunocompromised patients.",

    # Recovery and Prognosis
    "Most healthy individuals recover from mild pneumonia within a few weeks.",
    "Recovery may take longer in older adults or people with chronic illnesses.",
    "Fatigue and mild cough can persist after the infection clears.",
    "Pulmonary rehabilitation may help patients recover lung function after severe pneumonia.",
    "Follow-up chest imaging may be recommended after severe or persistent pneumonia.",
    "Early diagnosis and proper treatment significantly improve survival rates.",

    # Special Populations
    "Children under five years old are particularly vulnerable to pneumonia.",
    "Elderly patients often experience more severe symptoms and complications.",
    "Immunocompromised individuals may develop unusual or opportunistic pneumonia infections.",
    "Pregnant women with pneumonia require careful monitoring to protect both mother and baby.",
    "People with HIV/AIDS have increased risk of Pneumocystis jirovecii pneumonia.",

    # Medical and Biological Information
    "Inflammation in pneumonia interferes with normal oxygen exchange in the lungs.",
    "White blood cells accumulate in infected lung tissue to fight pathogens.",
    "Bacterial toxins can damage lung tissue and trigger inflammation.",
    "Fever during pneumonia is part of the body's immune response to infection.",
    "Excess mucus production in pneumonia can obstruct airflow in the lungs.",
    "Hypoxemia refers to low oxygen levels caused by impaired lung function.",
    "The immune system plays a critical role in controlling respiratory infections.",

    # Emergency Indicators
    "Seek immediate medical attention if pneumonia causes difficulty breathing or chest pain.",
    "Bluish lips or fingertips may indicate dangerously low oxygen levels.",
    "Persistent high fever and confusion can signal severe infection.",
    "Rapid worsening of symptoms may require emergency hospitalization.",
    "Children with severe pneumonia may show grunting or chest retractions while breathing."
]
 # Lazy-loaded heavy objects
_model = None
_index = None
_lock = Lock()

def _ensure_loaded():
    global _model, _index
    if _model is not None and _index is not None:
        return
    with _lock:
        if _model is not None and _index is not None:
            return
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = _model.encode(docs)
        _index = faiss.IndexFlatL2(embeddings.shape[1])
        _index.add(np.array(embeddings))


def retrieve_docs(query, k=2):
    """Return top-k docs for query. Loads model/index on first call."""
    _ensure_loaded()
    query_vec = _model.encode([query])
    _, I = _index.search(np.array(query_vec), k)
    return [docs[i] for i in I[0]]