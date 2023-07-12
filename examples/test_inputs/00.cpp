#include <bits/stdc++.h>
using namespace std;

int main() {
  int t; cin >> t;
  while (t--) {
    int n; cin >> n;

    vector<int> a(n), b(n);
    for (auto& x : a) cin >> x;
    for (auto& x : b) cin >> x;

    priority_queue<int> qa(a.begin(), a.end()), qb(b.begin(), b.end());

    int ans = 0;
    while (!qa.empty()){
      if (qa.top() == qb.top()){
        qa.pop(); qb.pop();
        continue;
      }

      ans++;

      if (qa.top() > qb.top()){
        qa.push(to_string(qa.top()).size());
        qa.pop();
      } else {
        qb.push(to_string(qb.top()).size());
        qb.pop();
      }
    }

    cout << ans << endl;
  }

  return 0;
}