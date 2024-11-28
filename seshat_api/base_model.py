from typing import Optional, Union

from .constants import BASE_URL
from .models._base import BaseModel

__all__ = ["BaseAPICall"]


class _Paginated:
    """
    A class for paginating results from the API.

    Parameters
    ----------
    client : SeshatAPI
        The API client to use for requests.
    endpoint : str
        The endpoint to get results from.
    params : dict, optional
        The parameters to use in the request.
    count : int, optional
        The total count of items in the API.
    name : str, optional
        The name of the API.
    """

    def __init__(
        self,
        client,  #: SeshatAPI,
        endpoint: str,
        params: Optional[dict] = None,
        count: Optional[int] = None,
        name: Optional[str] = None,
        model: Optional[BaseModel] = None,
    ):
        self.client = client
        self.endpoint = endpoint
        self.params = params or {}
        self.count = count
        self.name = name
        self.model = model
        self.next_url = None
        self.previous_url = None
        self.results = []
        self._load_page(endpoint, self.params)

    def _load_page(self, url: str, params: dict) -> None:
        """
        Load a page of results from the API.

        Parameters
        ----------
        url : str
            The URL of the page to load.

        params : dict
            The parameters to use in the request.

        Returns
        -------
        None
        """
        response = self.client.get(url, params)
        self.next_url = (
            response.get("next").replace(BASE_URL, "")
            if response.get("next")
            else None
        )
        self.previous_url = (
            response.get("previous").replace(BASE_URL, "")
            if response.get("previous")
            else None
        )
        self.results.extend(response.get("results", []))

    def __iter__(self):
        """
        Iterate over the paginated results.

        Returns
        -------
        _Paginated
        """
        return self

    def __next__(self) -> BaseModel:
        """
        Get the next item in the paginated results.

        Raises
        ------
        StopIteration
            If there are no more results to get.
        """
        if not self.results and self.next_url:
            self._load_page(self.next_url, self.params)

        if not self.results:
            self._load_page(self.endpoint, self.params)
            raise StopIteration

        if self.model:
            return self.model(
                data=self.results.pop(0), count=self.count, name=self.name
            )

        return BaseModel(
            data=self.results.pop(0), count=self.count, name=self.name
        )


class BaseAPICall:
    """
    Base class for API calls.

    Parameters
    ----------
    client : SeshatAPI, optional
        The API client to use for requests.

    Attributes
    ----------
    client : SeshatAPI
        The API client to use for requests.
    objects : _Paginated
        The paginated items in the API.
    """

    def __init__(self, client=None):  # : SeshatAPI = None):
        self.client = client
        self._count = None

        # Check to see if a single model is defined
        try:
            self.model = self.SINGLE_MODEL
        except AttributeError:
            self.model = None

        self.page = _Paginated(
            self.client,
            self.ENDPOINT,
            count=self.count,
            name=self.name,
            model=self.model,
        )

    def __iter__(self) -> _Paginated:
        """
        Iterate over the items in the API.
        """
        return iter(self.page)

    def __len__(self) -> int:
        """
        Get the count of items in the API.
        """
        return self.count

    def __getitem__(self, index: Union[int, slice]) -> BaseModel:
        """
        Get a single item or a slice of items from the API.

        Parameters
        ----------
        index : int or slice
            The index of the item to get or a slice of items to get.

        Returns
        -------
        BaseModel or list of BaseModel

        Raises
        ------
        TypeError
            If index is not an int or slice.
        """
        if isinstance(index, int):
            if self.model:
                return self.model(
                    data=self.page.results[index],
                    count=self.count,
                    name=self.name,
                )

            return BaseModel(
                data=self.page.results[index],
                count=self.count,
                name=self.name,
            )

        if isinstance(index, slice):
            if self.model:
                return [
                    self.model(data=i, count=self.count, name=self.name)
                    for i in self.page.results[index]
                ]

            return [
                BaseModel(data=i, count=self.count, name=self.name)
                for i in self.page.results[index]
            ]

        raise TypeError("Index must be an integer or slice")

    def __repr__(self):
        """
        Get a string representation of the API.
        """
        return f"<{self.name}: {self.count}>"

    def __str__(self):
        """
        Get a string representation of the API.
        """
        return f"<{self.name}: {self.count}>"

    @property
    def name(self):
        """
        Get the name of the API class.
        """
        return self.__class__.__name__

    def get_page(self, page: int = 1) -> dict:
        """
        Get a specific page of items from the API.

        Parameters
        ----------
        page : int, optional
            The page number to get.

        Returns
        -------
        dict
            The page of items from the API.
        """
        return self.client.get(self.ENDPOINT, params={"page": page})

    @property
    def count(self) -> int:
        """
        Get the count of items in the API.

        Returns
        -------
        int
            The count of items in the API.
        """
        if not self._count:
            self._count = self.client.count(self.ENDPOINT)

        return self._count

    def get(self, id):
        """
        Fetch a single object by its ID.

        Args:
            id (str): The ID of the object to fetch.

        Returns:
            BaseModel: An instance of BaseModel representing the polity.
        """
        # Construct the endpoint
        endpoint = (
            self.ENDPOINT[:-1]
            if self.ENDPOINT.endswith("/")
            else self.ENDPOINT
        )
        endpoint += f"/{id}"

        # Get the data from the API
        data = self.client.get(endpoint)

        if self.model:
            return self.model(data=data, count=self.count, name=self.name)

        return BaseModel(data=data, count=self.count, name=self.name)
    
    def get_all(self):
        """
        Get all items from the API.

        Returns
        -------
        list
            A list of all items from the API.
        """
        all_results = []
        page = 1

        while True:
            try:
                response = self.get_page(page)
            except:
                break
            results = response.get('results', [])
            if not results:
                break
            for result in results:
                if result['id'] not in [r['id'] for r in all_results]:
                    all_results.append(result)
            page += 1

        return all_results
