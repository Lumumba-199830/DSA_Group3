class PoultryRecord {
    constructor(tagId, breed, age, weight, eggCount, healthStatus) {
        this.tagId = tagId;
        this.breed = breed;
        this.age = age;
        this.weight = weight;
        this.eggCount = eggCount;
        this.healthStatus = healthStatus;
        
        if (this.healthStatus === "Critical") {
            this.priority = 1; 
        } else if (this.healthStatus === "Sick") {
            this.priority = 2;
        } else {
            this.priority = 3; 
        }
    }
}

class HealthAlertMinHeap {
    constructor() {
        this.heap = []; 
    }

    getLeftChildIndex(parentIndex) { return 2 * parentIndex + 1; }
    getRightChildIndex(parentIndex) { return 2 * parentIndex + 2; }
    getParentIndex(childIndex) { return Math.floor((childIndex - 1) / 2); }

    swap(indexOne, indexTwo) {
        let temp = this.heap[indexOne];
        this.heap[indexOne] = this.heap[indexTwo];
        this.heap[indexTwo] = temp;
    }

    peek() {
        if (this.heap.length === 0) return null;
        return this.heap[0];
    }

    insert(bird) {
        if (bird.priority > 2) return; 
        this.heap.push(bird);
        this.bubbleUp(this.heap.length - 1);
    }

    bubbleUp(currentIndex) {
        while (currentIndex > 0) {
            let parentIndex = this.getParentIndex(currentIndex);

            if (this.heap[currentIndex].priority >= this.heap[parentIndex].priority) {
                break;
            }

            this.swap(currentIndex, parentIndex);
            currentIndex = parentIndex;
        }
    }

    extractMin() {
        if (this.heap.length === 0) return null;
        if (this.heap.length === 1) return this.heap.pop();

        const mostCritical = this.heap[0];
        this.heap[0] = this.heap.pop();
        this.sinkDown(0);

        return mostCritical;
    }

    sinkDown(currentIndex) {
        let length = this.heap.length;

        while (true) {
            let leftChildIndex = this.getLeftChildIndex(currentIndex);
            let rightChildIndex = this.getRightChildIndex(currentIndex);
            let smallestPriorityIndex = currentIndex;

            if (leftChildIndex < length && this.heap[leftChildIndex].priority < this.heap[smallestPriorityIndex].priority) {
                smallestPriorityIndex = leftChildIndex;
            }

            if (rightChildIndex < length && this.heap[rightChildIndex].priority < this.heap[smallestPriorityIndex].priority) {
                smallestPriorityIndex = rightChildIndex;
            }

            if (smallestPriorityIndex === currentIndex) break;

            this.swap(currentIndex, smallestPriorityIndex);
            currentIndex = smallestPriorityIndex;
        }
    }
} 

// --- TESTING THE SYSTEM ---
const healthSystem = new HealthAlertMinHeap();

const bird1 = new PoultryRecord("PF-001", "Broiler", 5, 1.2, 0, "Sick");
const bird2 = new PoultryRecord("PF-002", "Kienyeji", 12, 1.5, 30, "Critical");
const bird3 = new PoultryRecord("PF-003", "Layer", 20, 1.8, 120, "Healthy");
const bird4 = new PoultryRecord("PF-004", "Broiler", 4, 0.9, 0, "Critical");

healthSystem.insert(bird1); 
healthSystem.insert(bird2); 
healthSystem.insert(bird3); 
healthSystem.insert(bird4); 

console.log("Most urgent case:");
console.log(healthSystem.peek()); 

console.log("\nTreating bird and removing from alerts...");
const treatedBird = healthSystem.extractMin();
console.log(`Treated: ${treatedBird.tagId}`);

console.log("\nNext urgent case:");
console.log(healthSystem.peek());